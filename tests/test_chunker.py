"""
Tests for app/rag/chunker.py
Covers: chunk_text (plain) and chunk_text_with_metadata (Issue #1)
"""

import pytest
from app.rag.chunker import chunk_text, chunk_text_with_metadata, Chunk


# ---------------------------------------------------------------------------
# chunk_text
# ---------------------------------------------------------------------------

class TestChunkText:
    def test_basic_split(self):
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = chunk_text(text, chunk_size=50, overlap=0)
        assert len(chunks) == 2
        assert chunks[0].startswith("word0")
        assert chunks[1].startswith("word50")

    def test_overlap_produces_more_chunks(self):
        text = " ".join([f"w{i}" for i in range(100)])
        no_overlap = chunk_text(text, chunk_size=50, overlap=0)
        with_overlap = chunk_text(text, chunk_size=50, overlap=25)
        assert len(with_overlap) > len(no_overlap)

    def test_overlap_shares_words(self):
        """Last words of chunk N should appear at start of chunk N+1."""
        text = " ".join([f"w{i}" for i in range(20)])
        chunks = chunk_text(text, chunk_size=10, overlap=5)
        assert len(chunks) >= 2
        tail_of_first = chunks[0].split()[-5:]
        head_of_second = chunks[1].split()[:5]
        assert tail_of_first == head_of_second

    def test_empty_text_returns_empty(self):
        assert chunk_text("", chunk_size=500) == []

    def test_text_shorter_than_chunk_size(self):
        text = "hello world"
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == "hello world"

    def test_returns_list_of_strings(self):
        chunks = chunk_text("a b c d e", chunk_size=2, overlap=0)
        assert all(isinstance(c, str) for c in chunks)

    def test_no_empty_chunks(self):
        text = " ".join([f"w{i}" for i in range(50)])
        chunks = chunk_text(text, chunk_size=10, overlap=5)
        assert all(len(c.strip()) > 0 for c in chunks)


# ---------------------------------------------------------------------------
# chunk_text_with_metadata
# ---------------------------------------------------------------------------

class TestChunkTextWithMetadata:
    def test_returns_chunk_dataclasses(self):
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = chunk_text_with_metadata(text, chunk_size=50, overlap=0)
        assert all(isinstance(c, Chunk) for c in chunks)

    def test_index_is_sequential(self):
        text = " ".join([f"w{i}" for i in range(200)])
        chunks = chunk_text_with_metadata(text, chunk_size=50, overlap=10)
        for i, c in enumerate(chunks):
            assert c.index == i

    def test_word_count_matches_text(self):
        text = " ".join([f"w{i}" for i in range(100)])
        chunks = chunk_text_with_metadata(text, chunk_size=50, overlap=0)
        for c in chunks:
            assert c.word_count == len(c.text.split())

    def test_char_count_matches_text(self):
        text = " ".join([f"w{i}" for i in range(100)])
        chunks = chunk_text_with_metadata(text, chunk_size=50, overlap=0)
        for c in chunks:
            assert c.char_count == len(c.text)

    def test_start_end_word_range(self):
        text = " ".join([f"w{i}" for i in range(100)])
        chunks = chunk_text_with_metadata(text, chunk_size=50, overlap=0)
        assert chunks[0].start_word == 0
        assert chunks[0].end_word == 49
        assert chunks[1].start_word == 50

    def test_overlap_start_word_less_than_no_overlap(self):
        text = " ".join([f"w{i}" for i in range(200)])
        no_ov = chunk_text_with_metadata(text, chunk_size=50, overlap=0)
        with_ov = chunk_text_with_metadata(text, chunk_size=50, overlap=20)
        # Second chunk starts earlier with overlap
        assert with_ov[1].start_word < no_ov[1].start_word

    def test_empty_text_returns_empty(self):
        assert chunk_text_with_metadata("") == []

    def test_single_chunk_for_short_text(self):
        chunks = chunk_text_with_metadata("hello world foo bar", chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0].index == 0
