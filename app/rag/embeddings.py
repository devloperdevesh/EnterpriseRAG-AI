import hashlib
import json
import logging
from redis import Redis
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize a synchronous Redis client with connection pooling
try:
    redis_client = Redis(host="localhost", port=6379, db=0, socket_timeout=2)
except Exception as exc:
    logger.warning("Failed to initialize Redis client in embeddings: %s", exc)
    redis_client = None


def generate_embedding(text: str) -> list[float]:
    """
    Generate embedding for a given text.
    Uses a Redis cache to prevent redundant API calls / encoding overhead.
    """
    # 1. Generate a cache key using MD5 hash of the text
    text_bytes = text.encode("utf-8")
    text_hash = hashlib.md5(text_bytes).hexdigest()
    cache_key = f"embedding:{text_hash}"

    # 2. Try to get from Redis cache
    if redis_client:
        try:
            cached_val = redis_client.get(cache_key)
            if cached_val:
                logger.info("Embedding cache hit for text hash %s", text_hash)
                return json.loads(cached_val)
        except Exception as exc:
            logger.warning("Redis read error in generate_embedding: %s", exc)

    # 3. Cache miss: generate embedding
    logger.info("Embedding cache miss. Encoding text.")
    embedding = model.encode(text)
    embedding_list = embedding.tolist()

    # 4. Save to Redis cache (expire in 24 hours/86400 seconds)
    if redis_client:
        try:
            redis_client.setex(cache_key, 86400, json.dumps(embedding_list))
        except Exception as exc:
            logger.warning("Redis write error in generate_embedding: %s", exc)

    return embedding_list
