"""Qdrant client setup and collection management."""

import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    VectorParams, 
    Distance, 
    CollectionStatus,
    PointStruct,
    Filter,
    FieldCondition,
    Range,
    MatchValue,
    MatchAny
)
from .config import qdrant_config

logger = logging.getLogger(__name__)

class QdrantManager:
    """Manages Qdrant client connection and collection operations."""
    
    def __init__(self):
        self.client = QdrantClient(
            host=qdrant_config.host,
            port=qdrant_config.port
        )
        self.collection_name = qdrant_config.collection_name
        
    def create_collection(self, recreate: bool = False) -> bool:
        """Create the products collection with proper configuration."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(
                col.name == self.collection_name 
                for col in collections.collections
            )
            
            if collection_exists and recreate:
                logger.info(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
                collection_exists = False
            
            if not collection_exists:
                logger.info(f"Creating collection: {self.collection_name}")
                
                # Create collection with vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=qdrant_config.vector_size,
                        distance=Distance.COSINE
                    )
                )
                
                # Create payload indexes for efficient filtering
                self._create_payload_indexes()
                
                logger.info(f"Collection {self.collection_name} created successfully")
                return True
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                return True
                
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False
    
    def _create_payload_indexes(self):
        """Create indexes on structured fields for efficient filtering."""
        indexes = [
            ("category", "keyword"),
            ("brand", "keyword"),
            ("price", "float"),
            ("rating", "float"),
            ("availability", "keyword"),
            ("tags", "keyword")
        ]
        
        for field_name, field_type in indexes:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=field_type
                )
                logger.info(f"Created index for field: {field_name}")
            except Exception as e:
                logger.warning(f"Could not create index for {field_name}: {e}")
    
    def upsert_products(self, products: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """Insert or update products in the collection."""
        try:
            points = []
            for i, (product, embedding) in enumerate(zip(products, embeddings)):
                point = PointStruct(
                    id=i,  # Use index as ID for simplicity
                    vector=embedding,
                    payload={
                        "product_id": product["id"],
                        "title": product["title"],
                        "description": product["description"],
                        "category": product["category"],
                        "brand": product["brand"],
                        "price": product["price"],
                        "rating": product["rating"],
                        "num_reviews": product["num_reviews"],
                        "availability": product["availability"],
                        "tags": product["tags"],
                        "specifications": product["specifications"]
                    }
                )
                points.append(point)
            
            # Batch upsert
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size}")
            
            logger.info(f"Successfully upserted {len(points)} products")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting products: {e}")
            return False
    
    def search_products(
        self,
        query_vector: List[float],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search products using vector similarity and optional filters."""
        try:
            # Build filter conditions
            filter_conditions = self._build_filters(filters) if filters else None
            
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=filter_conditions,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            )
            
            # Format results
            results = []
            for hit in search_result:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    **hit.payload
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def _build_filters(self, filters: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from search parameters."""
        conditions = []
        
        if "category" in filters:
            conditions.append(
                FieldCondition(
                    key="category",
                    match=MatchValue(value=filters["category"])
                )
            )
        
        if "brand" in filters:
            conditions.append(
                FieldCondition(
                    key="brand",
                    match=MatchValue(value=filters["brand"])
                )
            )
        
        if "price_min" in filters or "price_max" in filters:
            price_range = Range(
                gte=filters.get("price_min", 0),
                lte=filters.get("price_max", float('inf'))
            )
            conditions.append(
                FieldCondition(
                    key="price",
                    range=price_range
                )
            )
        
        if "rating_min" in filters:
            conditions.append(
                FieldCondition(
                    key="rating",
                    range=Range(gte=filters["rating_min"])
                )
            )
        
        if "availability" in filters:
            conditions.append(
                FieldCondition(
                    key="availability",
                    match=MatchValue(value=filters["availability"])
                )
            )
        
        if "tags" in filters:
            if isinstance(filters["tags"], list):
                conditions.append(
                    FieldCondition(
                        key="tags",
                        match=MatchAny(any=filters["tags"])
                    )
                )
            else:
                conditions.append(
                    FieldCondition(
                        key="tags",
                        match=MatchValue(value=filters["tags"])
                    )
                )
        
        return Filter(must=conditions) if conditions else None
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "status": info.status,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}
    
    def close(self):
        """Close the client connection."""
        if hasattr(self.client, 'close'):
            self.client.close()
