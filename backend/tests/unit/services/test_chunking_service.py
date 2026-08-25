import pytest

from app.services.chunking_service import ChunkingService


def test_split_text_returns_empty_list_for_empty_text():
    service = ChunkingService()

    assert service.split_text("") == []
    assert service.split_text("   ") == []


def test_split_text_returns_single_chunk_for_short_text():
    service = ChunkingService(
        chunk_size=100,
        overlap=20,
    )

    text = "This is a short document."

    chunks = service.split_text(text)

    assert chunks == [text]


def test_split_text_creates_multiple_chunks():
    service = ChunkingService(
        chunk_size=10,
        overlap=2,
    )

    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = service.split_text(text)

    assert len(chunks) > 1


def test_split_text_respects_chunk_size():
    service = ChunkingService(
        chunk_size=10,
        overlap=2,
    )

    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = service.split_text(text)

    for chunk in chunks:
        assert len(chunk) <= 10


def test_split_text_creates_expected_overlap():
    service = ChunkingService(
        chunk_size=10,
        overlap=2,
    )

    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = service.split_text(text)

    assert chunks[0][-2:] == chunks[1][:2]


def test_split_text_preserves_all_content():
    service = ChunkingService(
        chunk_size=10,
        overlap=2,
    )

    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = service.split_text(text)

    reconstructed = chunks[0]

    for previous, current in zip(chunks, chunks[1:]):
        overlap = service.overlap
        reconstructed += current[overlap:]

    assert reconstructed == text


def test_invalid_chunk_size_raises_error():
    with pytest.raises(ValueError):
        ChunkingService(chunk_size=0)


def test_negative_overlap_raises_error():
    with pytest.raises(ValueError):
        ChunkingService(
            chunk_size=100,
            overlap=-1,
        )


def test_overlap_equal_to_chunk_size_raises_error():
    with pytest.raises(ValueError):
        ChunkingService(
            chunk_size=100,
            overlap=100,
        )


def test_overlap_greater_than_chunk_size_raises_error():
    with pytest.raises(ValueError):
        ChunkingService(
            chunk_size=100,
            overlap=150,
        )