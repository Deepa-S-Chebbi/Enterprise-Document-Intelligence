import random
import time

from google import genai
from google.genai import errors as genai_errors

from app.core.config import settings
from app.exceptions.extraction_exceptions import (
    LLMProviderError,
)

# Errors worth retrying: transient server-side unavailability / rate limiting.
_RETRYABLE_STATUS_CODES = {429, 503}


class GeminiClient:
    """
    Client for interacting with the Gemini API.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay_seconds: float = 1.0,
    ):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = settings.gemini_model
        self.max_retries = max_retries
        self.base_delay_seconds = base_delay_seconds

    def _is_retryable(self, exc: Exception) -> bool:
        status_code = getattr(exc, "code", None) or getattr(
            exc, "status_code", None
        )
        return status_code in _RETRYABLE_STATUS_CODES

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Sends a prompt to Gemini and returns the response text.

        Retries with exponential backoff + jitter on transient
        errors (429 rate limit, 503 model overloaded).
        """

        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                return response.text

            except genai_errors.APIError as e:
                last_error = e

                if not self._is_retryable(e) or attempt == self.max_retries:
                    raise LLMProviderError(
                        f"Gemini API Error: {e}"
                    ) from e

                delay = self.base_delay_seconds * (2 ** attempt)
                delay += random.uniform(0, delay * 0.25)
                time.sleep(delay)

            except Exception as e:
                raise LLMProviderError(
                    f"Gemini API Error: {e}"
                ) from e

        raise LLMProviderError(f"Gemini API Error: {last_error}")