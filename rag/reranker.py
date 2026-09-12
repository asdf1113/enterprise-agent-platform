from dataclasses import replace

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from rag.retriever import RetrievedChunk


class BgeReranker:
    def __init__(
        self,
        model_name: str,
        *,
        max_length: int,
    ) -> None:
        self.model_name = model_name
        self.max_length = max_length

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(model_name)
            .to("cpu")
            .eval()
        )

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        *,
        batch_size: int,
        top_k: int,
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        scored: list[RetrievedChunk] = []

        for start in range(
            0,
            len(chunks),
            batch_size,
        ):
            batch = chunks[
                start:start + batch_size
            ]

            inputs = self.tokenizer(
                [query] * len(batch),
                [chunk.content for chunk in batch],
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt",
            )

            with torch.inference_mode():
                logits = self.model(
                    **inputs
                ).logits.view(-1).float()

            scores = torch.sigmoid(logits).tolist()

            scored.extend(
                replace(
                    chunk,
                    rerank_score=float(score),
                )
                for chunk, score in zip(
                    batch,
                    scores,
                    strict=True,
                )
            )

        scored.sort(
            key=lambda chunk: (
                chunk.rerank_score
                if chunk.rerank_score is not None
                else float("-inf")
            ),
            reverse=True,
        )

        return scored[:top_k]
