from typing import List
from dataclasses import dataclass


@dataclass
class Chunk:
    index: int
    text: str
    word_count: int
    char_count: int
    start_word: int
    end_word: int


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping word-based chunks.
    Returns plain list of strings (used by existing pipeline).
    """
    words = text.split()
    chunks = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def chunk_text_with_metadata(
    text: str, chunk_size: int = 500, overlap: int = 50
) -> List[Chunk]:
    """
    Split text into overlapping chunks and return rich metadata per chunk.
    Used by the chunking visualization endpoint.
    """
    words = text.split()
    chunks: List[Chunk] = []
    step = max(1, chunk_size - overlap)

    for idx, i in enumerate(range(0, len(words), step)):
        chunk_words = words[i : i + chunk_size]
        chunk_text_str = " ".join(chunk_words)
        if not chunk_text_str:
            continue
        chunks.append(
            Chunk(
                index=idx,
                text=chunk_text_str,
                word_count=len(chunk_words),
                char_count=len(chunk_text_str),
                start_word=i,
                end_word=i + len(chunk_words) - 1,
            )
        )

    return chunks
