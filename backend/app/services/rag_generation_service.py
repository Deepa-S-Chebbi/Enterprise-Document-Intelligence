from app.llm.client import GeminiClient


class RAGGenerationService:
    """
    Generates answers using retrieved document context.
    """

    def __init__(
        self,
        llm_client: GeminiClient | None = None,
    ):
        self.llm_client = llm_client or GeminiClient()

    def generate_answer(
        self,
        query: str,
        context: list[str],
    ) -> str:
        """
        Generate an answer using the supplied document context.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if not context:
            raise ValueError("Context cannot be empty.")

        cleaned_context = [
            item.strip()
            for item in context
            if item and item.strip()
        ]

        if not cleaned_context:
            raise ValueError(
                "Context cannot contain only empty values."
            )

        formatted_context = "\n\n".join(
            f"[Document Context {index}]\n{chunk}"
            for index, chunk in enumerate(
                cleaned_context,
                start=1,
            )
        )

        prompt = f"""
You are an enterprise document question-answering assistant.

Answer the user's question using ONLY the provided document context.

If the answer cannot be found in the context, clearly say:
"I could not find the answer in the provided documents."

Do not invent facts.
Do not use outside knowledge.
Keep the answer concise and factual.

Document Context:
{formatted_context}

User Question:
{query}

Answer:
""".strip()

        return self.llm_client.generate(prompt)