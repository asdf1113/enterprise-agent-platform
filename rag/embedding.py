from sentence_transformers import SentenceTransformer


BGE_M3_DIMENSION = 1024


class BgeM3Embedder:
    def __init__(
        self,
        model_name: str,
        *,
        max_sequence_length: int,
    ) -> None:
        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name,
            device="cpu",
        )

        self.model.max_seq_length = (
            max_sequence_length
        )

    def encode(
        self,
        texts: list[str],
        *,
        batch_size: int,
    ) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        if embeddings.ndim != 2:
            raise ValueError(
                "Expected 2-dimensional embeddings"
            )

        if embeddings.shape[1] != BGE_M3_DIMENSION:
            raise ValueError(
                "Unexpected embedding dimension: "
                f"{embeddings.shape[1]}"
            )

        return embeddings.tolist()
