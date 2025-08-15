"""Embedding service for product descriptions using sentence transformers."""

import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from .config import embedding_config

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings from product text."""
    
    def __init__(self):
        """Initialize the embedding model."""
        logger.info(f"Loading embedding model: {embedding_config.model_name}")
        self.model = SentenceTransformer(embedding_config.model_name)
        self.model_name = embedding_config.model_name
        self.max_length = embedding_config.max_length
        self.batch_size = embedding_config.batch_size
        
        logger.info(f"Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def encode_products(self, products: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings for product descriptions."""
        try:
            # Combine title and description for richer embeddings
            texts = []
            for product in products:
                combined_text = f"{product['title']}. {product['description']}"
                # Add category and brand for better context
                combined_text += f" Category: {product['category']}. Brand: {product['brand']}."
                # Add key tags for additional context
                if product.get('tags'):
                    key_tags = product['tags'][:3]  # Use first 3 tags
                    combined_text += f" Tags: {', '.join(key_tags)}."
                
                texts.append(combined_text[:self.max_length])
            
            logger.info(f"Encoding {len(texts)} product descriptions...")
            
            # Generate embeddings in batches
            embeddings = []
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                batch_embeddings = self.model.encode(
                    batch_texts,
                    convert_to_numpy=True,
                    show_progress_bar=True if i == 0 else False
                )
                embeddings.extend(batch_embeddings.tolist())
                
                if (i // self.batch_size + 1) % 10 == 0:
                    logger.info(f"Processed batch {i // self.batch_size + 1}/{(len(texts) + self.batch_size - 1) // self.batch_size}")
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def encode_query(self, query: str) -> List[float]:
        """Generate embedding for a search query."""
        try:
            # Preprocess query to match product text format
            processed_query = query.strip()
            
            # Generate embedding
            embedding = self.model.encode([processed_query], convert_to_numpy=True)
            return embedding[0].tolist()
            
        except Exception as e:
            logger.error(f"Error encoding query '{query}': {e}")
            return []
    
    def get_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def encode_text_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode a batch of arbitrary texts."""
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 100
            )
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error encoding text batch: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "max_sequence_length": getattr(self.model, 'max_seq_length', 'Unknown'),
            "batch_size": self.batch_size
        }

# Global embedding service instance
embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance."""
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
    return embedding_service
