"""Image analysis tool using vision-capable LLM."""
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, BinaryContent
from supabase import Client
import base64
import os

from config import settings


async def image_analysis_tool(supabase: Client, document_id: str, query: str) -> str:
    """Analyze an image using a vision-capable LLM.

    Args:
        supabase: The Supabase client.
        document_id: The ID of the image document.
        query: What to extract from the image.

    Returns:
        Analysis result as text.
    """
    try:
        model = OpenAIModel(
            settings.vision_llm_choice,
            provider=OpenAIProvider(
                base_url=settings.llm_base_url,
                api_key=settings.llm_api_key,
            ),
        )
        vision_agent = Agent(
            model,
            system_prompt="You are an image analyzer who looks at images provided and answers the accompanying query in detail.",
        )

        result = (
            supabase.from_("documents")
            .select("metadata")
            .eq("metadata->>file_id", document_id)
            .limit(1)
            .execute()
        )

        if not result.data:
            return f"No content found for document: {document_id}"

        metadata = result.data[0]["metadata"]
        binary_str = metadata.get("file_contents")
        mime_type = metadata.get("mime_type")

        if not binary_str:
            return f"No file contents found for document: {document_id}"

        binary = base64.b64decode(binary_str.encode("utf-8"))
        analysis = await vision_agent.run(
            [query, BinaryContent(data=binary, media_type=mime_type)]
        )
        return analysis.data

    except Exception as e:
        return f"Error analyzing image: {e}"
