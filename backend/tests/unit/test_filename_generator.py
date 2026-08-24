from uuid import UUID

from app.utils.filename_generator import generate_unique_filename


def test_generate_unique_filename_preserves_extension():
    document_id, generated_filename = generate_unique_filename(
        "invoice.pdf"
    )

    assert generated_filename == f"{document_id}.pdf"


def test_generate_unique_filename_normalizes_extension():
    document_id, generated_filename = generate_unique_filename(
        "invoice.PDF"
    )

    assert generated_filename == f"{document_id}.pdf"


def test_generate_unique_filename_returns_valid_uuid():
    document_id, _ = generate_unique_filename("invoice.pdf")

    UUID(document_id)


def test_generate_unique_filename_generates_unique_ids():
    document_id_1, filename_1 = generate_unique_filename("invoice.pdf")
    document_id_2, filename_2 = generate_unique_filename("invoice.pdf")

    assert document_id_1 != document_id_2
    assert filename_1 != filename_2
    