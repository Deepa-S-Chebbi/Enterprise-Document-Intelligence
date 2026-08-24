from app.schemas.ocr import OCRPage, OCRResponse


def test_ocr_page_accepts_valid_data():
    page = OCRPage(
        page_number=1,
        extracted_text="Invoice Number: INV-001",
        average_confidence=0.94,
    )

    assert page.page_number == 1
    assert page.extracted_text == "Invoice Number: INV-001"
    assert page.average_confidence == 0.94


def test_ocr_response_accepts_valid_data():
    response = OCRResponse(
        filename="document.pdf",
        page_count=2,
        pages=[
            OCRPage(
                page_number=1,
                extracted_text="Page one text",
                average_confidence=0.95,
            ),
            OCRPage(
                page_number=2,
                extracted_text="Page two text",
                average_confidence=0.91,
            ),
        ],
        processing_time=2.5,
        status="success",
    )

    assert response.filename == "document.pdf"
    assert response.page_count == 2
    assert len(response.pages) == 2
    assert response.status == "success"


def test_ocr_response_accepts_empty_pages():
    response = OCRResponse(
        filename="empty.pdf",
        page_count=0,
        pages=[],
        processing_time=0.1,
        status="success",
    )

    assert response.pages == []