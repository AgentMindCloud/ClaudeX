"""Lightweight JSON Schema validator + Python-signature → schema inference.

Keeps Phase 2 zero-dep. The validator supports the subset of Draft-07 we
actually need to police tool-call arguments coming back from the model:

  * ``type`` (string or list)
  * ``properties`` / ``required`` / ``additionalProperties`` (bool)
  * ``items`` for arrays
  * ``enum``
  * ``minimum`` / ``maximum`` (numbers)
  * ``minLength`` / ``maxLength`` (strings)

Unknown keywords are ignored rather than rejected — the intent is to catch
real shape mistakes, not enforce spec strictness.
"""

from __future__ import annotations

import enum
import inspect
import types
import typing
from typing import Any, Union, get_args, get_origin


class SchemaError(ValueError):
    """Raised when a value does not match its JSON Schema."""


_PY_TO_JSON: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
    type(None): "null",
}

_JSON_TYPE_CHECKS: dict[str, Any] = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------
def validate(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    if not isinstance(schema, dict):
        raise SchemaError(f"{path}: schema must be a dict, got {type(schema).__name__}")

    # type
    t = schema.get("type")
    if isinstance(t, str):
        _check_type(value, t, path)
    elif isinstance(t, list):
        if not any(_JSON_TYPE_CHECKS.get(tn, lambda _v: False)(value) for tn in t):
            raise SchemaError(f"{path}: expected one of {t}, got {type(value).__name__}")

    # enum
    if "enum" in schema and value not in schema["enum"]:
        raise SchemaError(f"{path}: {value!r} not in enum {schema['enum']!r}")

    # numeric bounds
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise SchemaError(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            raise SchemaError(f"{path}: {value} > maximum {schema['maximum']}")

    # string bounds
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise SchemaError(f"{path}: length {len(value)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise SchemaError(f"{path}: length {len(value)} > maxLength {schema['maxLength']}")

    # arrays
    if isinstance(value, list) and "items" in schema:
        item_schema = schema["items"]
        for i, item in enumerate(value):
            validate(item, item_schema, f"{path}[{i}]")

    # objects
    if isinstance(value, dict):
        properties = schema.get("properties") or {}
        required = schema.get("required") or []
        for key in required:
            if key not in value:
                raise SchemaError(f"{path}: missing required property {key!r}")
        additional = schema.get("additionalProperties", True)
        for key, val in value.items():
            if key in properties:
                validate(val, properties[key], f"{path}.{key}")
            elif additional is False:
                raise SchemaError(f"{path}: unexpected property {key!r}")
            elif isinstance(additional, dict):
                validate(val, additional, f"{path}.{key}")


def _check_type(value: Any, json_type: str, path: str) -> None:
    check = _JSON_TYPE_CHECKS.get(json_type)
    if check is None:
        return  # unknown type keyword; be permissive
    if not check(value):
        raise SchemaError(
            f"{path}: expected {json_type}, got {type(value).__name__}"
        )


# ---------------------------------------------------------------------------
# signature → JSON schema
# ---------------------------------------------------------------------------
def infer_schema(func: Any) -> dict[str, Any]:
    """Infer a JSON Schema ``object`` for ``func``'s keyword parameters."""
    sig = inspect.signature(func)
    hints = typing.get_type_hints(func, include_extras=True)

    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        annotation = hints.get(name, param.annotation)
        prop_schema, optional = _annotation_to_schema(annotation)
        if param.default is not inspect.Parameter.empty:
            optional = True
            prop_schema.setdefault("default", _jsonable_default(param.default))
        properties[name] = prop_schema
        if not optional:
            required.append(name)

    out: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        out["required"] = required
    out["additionalProperties"] = False
    return out


def _annotation_to_schema(ann: Any) -> tuple[dict[str, Any], bool]:
    """Return (schema_dict, is_optional)."""
    if ann is inspect.Parameter.empty or ann is Any:
        return {}, False

    origin = get_origin(ann)

    # typing.Optional[T] / Union[..., None] / PEP 604 `A | B`
    if origin is Union or origin is types.UnionType:
        args = [a for a in get_args(ann) if a is not type(None)]
        is_opt = len(args) != len(get_args(ann))
        if len(args) == 1:
            inner, _ = _annotation_to_schema(args[0])
            return inner, is_opt
        schemas = [_annotation_to_schema(a)[0] for a in args]
        # If all inner schemas have a plain "type", fold into a type list.
        inner_types = [s.get("type") for s in schemas]
        if all(isinstance(t, str) for t in inner_types):
            return {"type": inner_types}, is_opt
        return {"anyOf": schemas}, is_opt

    # Literal[...]
    if origin is typing.Literal:
        values = list(get_args(ann))
        inner_types = {_PY_TO_JSON.get(type(v), "string") for v in values}
        out: dict[str, Any] = {"enum": values}
        if len(inner_types) == 1:
            out["type"] = next(iter(inner_types))
        return out, False

    # list[T] / List[T]
    if origin in (list, typing.List):  # noqa: UP006
        args = get_args(ann)
        item_schema, _ = _annotation_to_schema(args[0]) if args else ({}, False)
        return {"type": "array", "items": item_schema}, False

    # dict[K, V] / Dict
    if origin in (dict, typing.Dict):  # noqa: UP006
        return {"type": "object"}, False

    # Enum subclass
    if isinstance(ann, type) and issubclass(ann, enum.Enum):
        values = [e.value for e in ann]
        inner_types = {_PY_TO_JSON.get(type(v), "string") for v in values}
        out = {"enum": values}
        if len(inner_types) == 1:
            out["type"] = next(iter(inner_types))
        return out, False

    # plain types
    if isinstance(ann, type):
        mapped = _PY_TO_JSON.get(ann)
        if mapped is not None:
            return {"type": mapped}, False

    # Unknown annotation — emit an empty schema so we don't falsely reject.
    return {}, False


def _jsonable_default(v: Any) -> Any:
    if isinstance(v, enum.Enum):
        return v.value
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, (list, tuple)):
        return [_jsonable_default(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _jsonable_default(x) for k, x in v.items()}
    return repr(v)
