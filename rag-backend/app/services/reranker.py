import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class Reranker:
    def __init__(self):
        self.MODEL_NAME = 'BAAI/bge-reranker-v2-m3'
        self.tokenizer = self._load_tokenizer()
        self.model = self._load_model()
        self.model.eval()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _load_tokenizer(self):
        logger.info(f"Loading reranker tokenizer for {self.MODEL_NAME}")
        return AutoTokenizer.from_pretrained(self.MODEL_NAME)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _load_model(self):
        logger.info(f"Loading reranker model {self.MODEL_NAME}")
        return AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME)

    def rerank_chunks(self, question: str, chunks: List[str], score_threshold: float = 1.0, return_debug: bool = False) -> List[str]:
        pairs = [[question, chunk] for chunk in chunks]
        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
            scores = self.model(**inputs, return_dict=True).logits.view(-1).float()

        # Filter and sort by score
        scored_pairs = sorted(
            [(score.item(), chunk) for score, chunk in zip(scores, chunks) if score.item() >= score_threshold],
            key=lambda x: x[0],
            reverse=True
        )

        if return_debug:
            print("🔍 Reranker Scores:")
            for score, chunk in scored_pairs:
                print(f"Score: {score:.2f} | Chunk: {chunk[:80]}...")

        return [chunk for _, chunk in scored_pairs]

reranker = Reranker() 