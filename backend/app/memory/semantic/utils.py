from .model import get_model
from sklearn.metrics.pairwise import cosine_similarity

model = get_model()

def pairwise_similarity(text1: str, text2: str):
    """
    Compute cosine similarity between two text inputs.

    Cosine similarity measures how semantically similar two
    embeddings are in vector space.

    Similarity Range:
        1.0   -> identical meaning
        0.0   -> unrelated
        -1.0  -> opposite direction (rare in embeddings)

    Args:
        text1 (str):
            First text input.

        text2 (str):
            Second text input.

    Returns:
        float:
            Cosine similarity score.

    Example:
        >>> pairwise_similarity(
        ...     "Student struggles with recursion",
        ...     "Student has difficulty with recursive functions"
        ... )
        0.82

    Notes:
        - Higher score = greater semantic similarity.
        - Useful for debugging embedding quality.
        - This does NOT use ChromaDB.
    """
    e1 = model.encode(text1)
    e2 = model.encode(text2)
    return cosine_similarity([e1], [e2])[0][0]
