from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.MODEL_NAME = "BAAI/bge-base-en-v1.5"
        self.tokenizer = self._load_tokenizer()
        self.model = self._load_model()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _load_tokenizer(self):
        logger.info(f"Loading tokenizer for {self.MODEL_NAME}")
        return AutoTokenizer.from_pretrained(self.MODEL_NAME)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _load_model(self):
        logger.info(f"Loading model {self.MODEL_NAME}")
        return AutoModel.from_pretrained(self.MODEL_NAME)

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]  # First element is the last hidden state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return (token_embeddings * input_mask_expanded).sum(1) / input_mask_expanded.sum(1)

    async def embed_texts(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Tokenize the batch
            encoded_input = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )

            # Move to GPU/CPU
            encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}

            # Forward pass
            with torch.no_grad():
                model_output = self.model(**encoded_input)

            # Pooling
            embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

            # Normalize
            embeddings = F.normalize(embeddings, p=2, dim=1)

            # Convert embeddings to list of floats and append
            all_embeddings.extend(embeddings.cpu().tolist())

        return all_embeddings

embedding_service = EmbeddingService() 