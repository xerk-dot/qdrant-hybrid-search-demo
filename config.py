"""Configuration settings for the Qdrant e-commerce search demo."""

import os
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class QdrantConfig:
    """Qdrant connection and collection configuration."""
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "ecommerce_products"
    vector_size: int = 384  # all-MiniLM-L6-v2 embedding dimension
    distance_metric: str = "Cosine"
    
@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""
    model_name: str = "all-MiniLM-L6-v2"
    max_length: int = 512
    batch_size: int = 32
    
@dataclass
class SearchConfig:
    """Search and scoring configuration."""
    default_limit: int = 15
    similarity_threshold: float = 0.3
    
    # Scoring weights for hybrid search
    semantic_weight: float = 0.7
    rating_weight: float = 0.2
    popularity_weight: float = 0.1
    
    # Price range mappings
    price_ranges: Dict[str, tuple] = None
    
    def __post_init__(self):
        if self.price_ranges is None:
            self.price_ranges = {
                "budget": (0, 50),
                "mid-range": (50, 200),
                "premium": (200, 500),
                "luxury": (500, float('inf'))
            }

@dataclass
class DemoConfig:
    """Demo application configuration."""
    app_title: str = "Qdrant E-commerce Search Demo"
    sample_queries: List[str] = None
    categories: List[str] = None
    
    def __post_init__(self):
        if self.sample_queries is None:
            self.sample_queries = [
                "comfortable running shoes",
                "wireless noise canceling headphones",
                "gaming laptop under $1000",
                "waterproof bluetooth speaker",
                "ergonomic office chair",
                "4K webcam for streaming",
                "portable power bank",
                "fitness tracker with GPS"
            ]
            
        if self.categories is None:
            self.categories = [
                "Electronics",
                "Clothing & Accessories", 
                "Sports & Outdoors",
                "Home & Garden",
                "Books",
                "Beauty & Personal Care",
                "Toys & Games",
                "Automotive"
            ]

# Global configuration instances
qdrant_config = QdrantConfig()
embedding_config = EmbeddingConfig()
search_config = SearchConfig()
demo_config = DemoConfig()
