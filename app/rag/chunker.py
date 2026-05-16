def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks


def chunk_text_with_overlap(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    step = max(chunk_size - overlap, 1)

    for i in range(0, len(words), step):
        end = min(i + chunk_size, len(words))
        chunk_words = words[i:end]
        chunks.append({
            "index": len(chunks),
            "text": " ".join(chunk_words),
            "start_word": i,
            "end_word": end,
            "word_count": len(chunk_words),
            "overlap_prev": overlap if i > 0 else 0,
            "overlap_next": overlap if end < len(words) else 0,
        })

        if end == len(words):
            break

    return chunks
