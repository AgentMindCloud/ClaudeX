from enum import Enum
from typing import Any, Literal, Optional

import pytest

from frok.tools.schema import SchemaError, infer_schema, validate


# ---------------------------------------------------------------------------
# validate()
# ---------------------------------------------------------------------------
def test_validate_type_and_required():
    schema = {
        "type": "object",
        "properties": {"q": {"type": "string"}, "k": {"type": "integer"}},
        "required": ["q"],
        "additionalProperties": False,
    }
    validate({"q": "grok", "k": 5}, schema)
    validate({"q": "grok"}, schema)
    with pytest.raises(SchemaError, match="required property 'q'"):
        validate({"k": 1}, schema)
    with pytest.raises(SchemaError, match="expected integer"):
        validate({"q": "x", "k": "nope"}, schema)
    with pytest.raises(SchemaError, match="unexpected property 'extra'"):
        validate({"q": "x", "extra": 1}, schema)


def test_validate_distinguishes_bool_from_int():
    with pytest.raises(SchemaError):
        validate(True, {"type": "integer"})
    with pytest.raises(SchemaError):
        validate(1, {"type": "boolean"})


def test_validate_enum_and_ranges():
    schema = {"type": "integer", "enum": [1, 2, 3], "minimum": 1, "maximum": 3}
    validate(2, schema)
    with pytest.raises(SchemaError, match="not in enum"):
        validate(4, {"type": "integer", "enum": [1, 2, 3]})
    with pytest.raises(SchemaError, match="minimum"):
        validate(0, {"type": "integer", "minimum": 1})


def test_validate_array_items():
    schema = {"type": "array", "items": {"type": "string"}}
    validate(["a", "b"], schema)
    with pytest.raises(SchemaError, match=r"\[1\]"):
        validate(["a", 2], schema)


def test_validate_nested_object():
    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
                "required": ["id"],
            }
        },
    }
    validate({"user": {"id": 7}}, schema)
    with pytest.raises(SchemaError, match=r"\$.user: missing required property 'id'"):
        validate({"user": {}}, schema)


# ---------------------------------------------------------------------------
# infer_schema()
# ---------------------------------------------------------------------------
def test_infer_basic_signature():
    def fn(query: str, limit: int = 5, verbose: bool = False): ...

    schema = infer_schema(fn)
    assert schema["type"] == "object"
    assert schema["properties"]["query"] == {"type": "string"}
    assert schema["properties"]["limit"]["type"] == "integer"
    assert schema["properties"]["limit"]["default"] == 5
    assert schema["required"] == ["query"]
    assert schema["additionalProperties"] is False


def test_infer_optional_and_union():
    def fn(x: Optional[int] = None, y: str | int = "z"): ...

    schema = infer_schema(fn)
    assert "x" not in schema.get("required", [])
    # Optional[int] collapses to just int (optional)
    assert schema["properties"]["x"] == {"type": "integer", "default": None}
    # str | int → {"type": ["string", "integer"]}
    assert set(schema["properties"]["y"]["type"]) == {"string", "integer"}


def test_infer_list_and_literal_and_enum():
    class Kind(Enum):
        RED = "red"
        BLUE = "blue"

    def fn(tags: list[str], mode: Literal["fast", "slow"], color: Kind): ...

    schema = infer_schema(fn)
    assert schema["properties"]["tags"] == {"type": "array", "items": {"type": "string"}}
    assert schema["properties"]["mode"] == {"type": "string", "enum": ["fast", "slow"]}
    assert schema["properties"]["color"]["enum"] == ["red", "blue"]


def test_infer_unknown_annotation_is_permissive():
    def fn(thing: Any, blob): ...  # Any + no annotation

    schema = infer_schema(fn)
    assert schema["properties"]["thing"] == {}
    assert schema["properties"]["blob"] == {}
    assert schema["required"] == ["thing", "blob"]
