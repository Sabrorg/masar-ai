"""
Embeddings module for text encoding
"""
from typing import List, Optional
from pathlib import Path
import torch
from hr_agent.utils import get_device, get_logger

logger = get_logger(__name__)

class EmbeddingModel:
    """
    Wrapper for local embedding models
    """

    def __init__(
        self,
        model_path: Path,
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        self.model_path = model_path
        self.device = device or get_device()
        self.batch_size = batch_size
        self.model = None
        self.tokenizer = None

        self._load_model()

    def _load_model(self):
        """Load embedding model"""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Embedding model not found at: {self.model_path}\n"
                f"Please download the model (e.g., BAAI/bge-m3) and place it at this location."
            )

        try:
            from transformers import AutoTokenizer, AutoModel

            logger.info(f"Loading embedding model from {self.model_path}")
            logger.info(f"Using device: {self.device}")

            self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
            self.model = AutoModel.from_pretrained(
                str(self.model_path),
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map=self.device if self.device == "cuda" else None
            )

            if self.device == "cpu":
                self.model = self.model.to("cpu")

            self.model.eval()
            logger.info("✓ Embedding model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def encode(self, texts: List[str], show_progress: bool = False) -> List[List[float]]:
        """
        Encode texts to embeddings
        """
        if not texts:
            return []

        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]

            with torch.no_grad():
                # Tokenize
                inputs = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                )

                # Move to device
                if self.device == "cuda":
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}

                # Get embeddings
                outputs = self.model(**inputs)

                # Mean pooling
                embeddings = self._mean_pooling(outputs, inputs['attention_mask'])

                # Normalize
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

                # Convert to list
                embeddings_list = embeddings.cpu().tolist()
                all_embeddings.extend(embeddings_list)

            if show_progress and (i + self.batch_size) % 100 == 0:
                logger.info(f"Encoded {min(i + self.batch_size, len(texts))}/{len(texts)} texts")

        return all_embeddings

    def _mean_pooling(self, model_output, attention_mask):
        """Mean pooling with attention mask"""
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def encode_single(self, text: str) -> List[float]:
        """Encode a single text"""
        return self.encode([text])[0]

def create_embedding_model(
    model_path: Path,
    device: Optional[str] = None
) -> EmbeddingModel:
    """Factory function to create embedding model"""
    return EmbeddingModel(model_path, device)
