from unittest.mock import MagicMock
from uuid import uuid4

from app.services.document_query_service import DocumentQueryService


def create_service():
    document_repo = MagicMock()
    ocr_repo = MagicMock()
    extraction_repo = MagicMock()

    service = DocumentQueryService(
        document_repo=document_repo,
        ocr_repo=ocr_repo,
        extraction_repo=extraction_repo,
    )

    return (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    )


def test_get_document_returns_complete_document_data():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document_id = uuid4()

    document = MagicMock()
    ocr_result = MagicMock()
    extraction_result = MagicMock()

    document_repo.get_by_id.return_value = document
    ocr_repo.get_by_document_id.return_value = ocr_result
    extraction_repo.get_by_document_id.return_value = (
        extraction_result
    )

    result = service.get_document(document_id)

    assert result == {
        "document": document,
        "ocr": ocr_result,
        "extraction": extraction_result,
    }

    document_repo.get_by_id.assert_called_once_with(
        document_id
    )

    ocr_repo.get_by_document_id.assert_called_once_with(
        document_id
    )

    extraction_repo.get_by_document_id.assert_called_once_with(
        document_id
    )


def test_get_document_returns_none_when_document_not_found():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document_id = uuid4()

    document_repo.get_by_id.return_value = None

    result = service.get_document(document_id)

    assert result is None

    document_repo.get_by_id.assert_called_once_with(
        document_id
    )

    ocr_repo.get_by_document_id.assert_not_called()
    extraction_repo.get_by_document_id.assert_not_called()


def test_get_document_allows_missing_ocr_result():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document_id = uuid4()

    document = MagicMock()
    extraction_result = MagicMock()

    document_repo.get_by_id.return_value = document
    ocr_repo.get_by_document_id.return_value = None
    extraction_repo.get_by_document_id.return_value = (
        extraction_result
    )

    result = service.get_document(document_id)

    assert result["document"] is document
    assert result["ocr"] is None
    assert result["extraction"] is extraction_result


def test_get_document_allows_missing_extraction_result():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    document_id = uuid4()

    document = MagicMock()
    ocr_result = MagicMock()

    document_repo.get_by_id.return_value = document
    ocr_repo.get_by_document_id.return_value = ocr_result
    extraction_repo.get_by_document_id.return_value = None

    result = service.get_document(document_id)

    assert result["document"] is document
    assert result["ocr"] is ocr_result
    assert result["extraction"] is None


def test_list_documents_passes_pagination_parameters():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    documents = [
        MagicMock(),
        MagicMock(),
    ]

    document_repo.list_all.return_value = documents

    result = service.list_documents(
        skip=10,
        limit=20,
    )

    assert result == documents

    document_repo.list_all.assert_called_once_with(
        skip=10,
        limit=20,
    )


def test_list_documents_uses_default_pagination():
    (
        service,
        document_repo,
        ocr_repo,
        extraction_repo,
    ) = create_service()

    documents = [MagicMock()]

    document_repo.list_all.return_value = documents

    result = service.list_documents()

    assert result == documents

    document_repo.list_all.assert_called_once_with(
        skip=0,
        limit=50,
    )