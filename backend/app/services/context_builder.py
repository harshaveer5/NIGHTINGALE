def build_context(retrieved_chunks: list):
    context_parts = []

    if retrieved_chunks:
        for index, chunk in enumerate(retrieved_chunks, start=1):
            context_parts.append(
                "\n".join(
                    [
                        f"Source {index}",
                        f"Document ID: {chunk['document_id']}",
                        f"Filename: {chunk.get('filename') or 'Unknown'}",
                        f"Chunk Index: {chunk['chunk_index']}",
                        f"Relevance Score: {chunk.get('score', 1.0):.3f}",
                        "Text:",
                        chunk["chunk_text"],
                    ]
                )
            )

    return "\n".join(context_parts)
