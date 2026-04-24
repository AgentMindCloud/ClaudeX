import math

import pytest

from frok.memory.embedder import HashEmbedder, cosine


async def test_hash_embedder_is_deterministic():
    e = HashEmbedder(dim=64)
    a = (await e.embed(["the curious frok ships code"]))[0]
    b = (await e.embed(["the curious frok ships code"]))[0]
    assert a == b
    # Unit-length (modulo float error)
    assert math.isclose(math.sqrt(sum(x * x for x in a)), 1.0, rel_tol=1e-6)


async def test_hash_embedder_similarity_orders_sensibly():
    e = HashEmbedder(dim=256)
    base = "grok seeks truth about the universe"
    near = "grok seeks truth about galaxies"
    far = "bake a sourdough loaf with rye flour"
    [vb, vn, vf] = await e.embed([base, near, far])
    assert cosine(vb, vn) > cosine(vb, vf)


async def test_empty_text_produces_zero_vector():
    e = HashEmbedder(dim=32)
    [v] = await e.embed([""])
    assert v == [0.0] * 32
    # cosine with zero vector is defined as 0.0, not NaN
    assert cosine(v, [1.0] + [0.0] * 31) == 0.0


def test_cosine_dim_mismatch_raises():
    with pytest.raises(ValueError):
        cosine([1.0, 0.0], [1.0, 0.0, 0.0])
