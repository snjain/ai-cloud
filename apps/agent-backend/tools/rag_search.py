"""RAG search tools using Supabase pgvector."""
from typing import List
from openai import AsyncOpenAI
from supabase import Client
import os


async def get_embedding(text: str, embedding_client: AsyncOpenAI) -> List[float]:
    """Get embedding vector from OpenAI."""
    embedding_model = os.getenv("EMBEDDING_MODEL_CHOICE", "text-embedding-3-small")
    try:
        response = await embedding_client.embeddings.create(
            model=embedding_model,
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536


async def retrieve_relevant_documents_tool(
    supabase: Client, embedding_client: AsyncOpenAI, user_query: str
) -> str:
    """Retrieve relevant document chunks with RAG via Supabase pgvector."""
    try:
        query_embedding = await get_embedding(user_query, embedding_client)

        result = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": 4,
            },
        ).execute()

        if not result.data:
            return "No relevant documents found."

        formatted_chunks = []
        for doc in result.data:
            meta = doc.get("metadata", {})
            chunk_text = f"""
# Document ID: {meta.get('file_id', 'unknown')}
# Document Title: {meta.get('file_title', 'unknown')}
# Document URL: {meta.get('file_url', 'unknown')}

{doc['content']}
"""
            formatted_chunks.append(chunk_text)

        return "\n\n---\n\n".join(formatted_chunks)
    except Exception as e:
        return f"Error retrieving documents: {e}"


async def list_documents_tool(supabase: Client) -> List[str]:
    """List all available documents from document_metadata table."""
    try:
        result = (
            supabase.from_("document_metadata")
            .select("id, title, schema, url")
            .execute()
        )
        return str(result.data)
    except Exception as e:
        return str([])


async def get_document_content_tool(supabase: Client, document_id: str) -> str:
    """Retrieve full content of a specific document by combining all chunks."""
    try:
        # Try by file_id (UUID for new docs, path for old docs)
        result = (
            supabase.from_("documents")
            .select("id, content, metadata")
            .eq("metadata->>file_id", document_id)
            .order("id")
            .execute()
        )

        # If not found, try by file_title
        if not result.data:
            result = (
                supabase.from_("documents")
                .select("id, content, metadata")
                .eq("metadata->>file_title", document_id)
                .order("id")
                .execute()
            )

        if not result.data:
            return f"No content found for document: {document_id}"

        document_title = result.data[0]["metadata"]["file_title"].split(" - ")[0]
        formatted_content = [f"# {document_title}\n"]

        for chunk in result.data:
            formatted_content.append(chunk["content"])

        return "\n\n".join(formatted_content)[:20000]
    except Exception as e:
        return f"Error retrieving document content: {e}"
