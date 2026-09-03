import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.exceptions.pipeline_exceptions import (
    PipelineExtractionStageError,
    PipelineIndexingStageError,
    PipelineOCRStageError,
)
from app.exceptions.upload_exceptions import (
    FileStorageError,
    FileTooLargeError,
    InvalidFileTypeError,
)


# Configure logging
setup_logging()

logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


# Configure CORS for the Vite frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(api_router, prefix="/api/v1")


# -----------------------------
# Exception Handlers
# -----------------------------


@app.exception_handler(InvalidFileTypeError)
async def invalid_file_type_handler(
    request: Request,
    exc: InvalidFileTypeError,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(FileTooLargeError)
async def file_too_large_handler(
    request: Request,
    exc: FileTooLargeError,
):
    return JSONResponse(
        status_code=413,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(FileStorageError)
async def file_storage_handler(
    request: Request,
    exc: FileStorageError,
):
    logger.error(
        "File storage error: %s",
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "The file could not be stored. Please try again later.",
        },
    )


@app.exception_handler(PipelineOCRStageError)
async def pipeline_ocr_handler(
    request: Request,
    exc: PipelineOCRStageError,
):
    logger.error(
        "OCR pipeline stage failed: %s",
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "stage": "ocr",
            "detail": (
                "Document OCR processing failed. "
                "Please try again later."
            ),
        },
    )


@app.exception_handler(PipelineIndexingStageError)
async def pipeline_indexing_handler(
    request: Request,
    exc: PipelineIndexingStageError,
):
    logger.error(
        "Semantic indexing pipeline stage failed: %s",
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "stage": "indexing",
            "detail": (
                "Document semantic indexing failed. "
                "Please try again later."
            ),
        },
    )


@app.exception_handler(PipelineExtractionStageError)
async def pipeline_extraction_handler(
    request: Request,
    exc: PipelineExtractionStageError,
):
    logger.error(
        "Extraction pipeline stage failed: %s",
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "stage": "extraction",
            "detail": (
                "Document information extraction failed. "
                "Please try again later."
            ),
        },
    )