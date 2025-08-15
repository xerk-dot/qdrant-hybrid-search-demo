"""Hybrid search engine combining semantic search with structured filtering."""

import logging
from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass
from qdrant_client import QdrantClient
from embedding_service import get_embedding_service
from qdrant_manager import QdrantManager
from config import search_config, demo_config

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Structured search result with scoring details."""
    product_id: str
    title: str
    description: str
    category: str
    brand: str
    price: float
    rating: float
    num_reviews: int
    availability: str
    tags: List[str]
    specifications: Dict[str, Any]
    
    # Scoring details
    semantic_score: float
    final_score: float
    score_breakdown: Dict[str, float]

class SearchEngine:
    """Hybrid search engine for e-commerce products."""
    
    def __init__(self):
        self.qdrant_manager = QdrantManager()
        self.embedding_service = get_embedding_service()
        
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = None,
        include_score_breakdown: bool = True
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic similarity with structured filtering.
        
        Args:
            query: Search query text
            filters: Structured filters (category, brand, price range, etc.)
            limit: Maximum number of results
            include_score_breakdown: Whether to include detailed scoring information
            
        Returns:
            List of SearchResult objects ranked by relevance
        """
        if limit is None:
            limit = search_config.default_limit
            
        try:
            # Parse query for implicit filters
            enhanced_filters = self._extract_query_filters(query, filters or {})
            
            # Generate query embedding
            query_embedding = self.embedding_service.encode_query(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search Qdrant
            raw_results = self.qdrant_manager.search_products(
                query_vector=query_embedding,
                filters=enhanced_filters,
                limit=limit * 2,  # Get more results for re-ranking
                score_threshold=search_config.similarity_threshold
            )
            
            if not raw_results:
                logger.info("No results found")
                return []
            
            # Apply custom scoring and re-ranking
            scored_results = self._apply_custom_scoring(raw_results, query, include_score_breakdown)
            
            # Sort by final score and limit
            scored_results.sort(key=lambda x: x.final_score, reverse=True)
            
            return scored_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
    
    def _extract_query_filters(self, query: str, existing_filters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract implicit filters from the query text."""
        enhanced_filters = existing_filters.copy()
        query_lower = query.lower()
        
        # Extract price ranges
        price_patterns = [
            (r'under \$?(\d+)', lambda m: {'price_max': int(m.group(1))}),
            (r'below \$?(\d+)', lambda m: {'price_max': int(m.group(1))}),
            (r'less than \$?(\d+)', lambda m: {'price_max': int(m.group(1))}),
            (r'over \$?(\d+)', lambda m: {'price_min': int(m.group(1))}),
            (r'above \$?(\d+)', lambda m: {'price_min': int(m.group(1))}),
            (r'more than \$?(\d+)', lambda m: {'price_min': int(m.group(1))}),
            (r'\$?(\d+)-\$?(\d+)', lambda m: {'price_min': int(m.group(1)), 'price_max': int(m.group(2))}),
            (r'between \$?(\d+) and \$?(\d+)', lambda m: {'price_min': int(m.group(1)), 'price_max': int(m.group(2))})
        ]
        
        for pattern, extractor in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                enhanced_filters.update(extractor(match))
                break
        
        # Extract rating requirements
        rating_patterns = [
            (r'(\d+\.?\d*)\+ stars?', lambda m: {'rating_min': float(m.group(1))}),
            (r'(\d+\.?\d*) stars? or better', lambda m: {'rating_min': float(m.group(1))}),
            (r'highly rated', lambda m: {'rating_min': 4.0}),
            (r'top rated', lambda m: {'rating_min': 4.5})
        ]
        
        for pattern, extractor in rating_patterns:
            match = re.search(pattern, query_lower)
            if match:
                enhanced_filters.update(extractor(match))
                break
        
        # Extract category hints
        category_keywords = {
            'laptop': 'Electronics',
            'computer': 'Electronics',
            'headphones': 'Electronics',
            'phone': 'Electronics',
            'camera': 'Electronics',
            'shirt': 'Clothing & Accessories',
            'shoes': 'Clothing & Accessories',
            'dress': 'Clothing & Accessories',
            'jacket': 'Clothing & Accessories',
            'running': 'Sports & Outdoors',
            'fitness': 'Sports & Outdoors',
            'outdoor': 'Sports & Outdoors',
            'camping': 'Sports & Outdoors',
            'furniture': 'Home & Garden',
            'kitchen': 'Home & Garden',
            'garden': 'Home & Garden',
            'decor': 'Home & Garden'
        }
        
        for keyword, category in category_keywords.items():
            if keyword in query_lower and 'category' not in enhanced_filters:
                enhanced_filters['category'] = category
                break
        
        # Extract brand mentions
        known_brands = [
            'apple', 'samsung', 'sony', 'nike', 'adidas', 'canon', 'dell', 'hp', 
            'lenovo', 'bose', 'calvin klein', 'coach', 'under armour', 'patagonia'
        ]
        
        for brand in known_brands:
            if brand in query_lower and 'brand' not in enhanced_filters:
                # Capitalize properly
                enhanced_filters['brand'] = brand.title()
                break
        
        return enhanced_filters
    
    def _apply_custom_scoring(
        self, 
        results: List[Dict[str, Any]], 
        query: str, 
        include_breakdown: bool
    ) -> List[SearchResult]:
        """Apply custom scoring logic combining multiple relevance signals."""
        scored_results = []
        
        for result in results:
            # Base semantic score from Qdrant
            semantic_score = result['score']
            
            # Calculate additional scoring factors
            score_breakdown = {
                'semantic': semantic_score * search_config.semantic_weight
            }
            
            # Rating boost (normalize to 0-1)
            rating_boost = (result['rating'] - 1.0) / 4.0  # Scale 1-5 to 0-1
            score_breakdown['rating'] = rating_boost * search_config.rating_weight
            
            # Popularity boost (based on number of reviews, log-scaled)
            import math
            max_reviews = 5000  # Assumed max from data generation
            popularity_boost = math.log(1 + result['num_reviews']) / math.log(1 + max_reviews)
            score_breakdown['popularity'] = popularity_boost * search_config.popularity_weight
            
            # Availability penalty
            availability_multiplier = 1.0
            if result['availability'] == 'Limited Stock':
                availability_multiplier = 0.9
            elif result['availability'] == 'Out of Stock':
                availability_multiplier = 0.5
            
            # Query-specific boosts
            query_lower = query.lower()
            title_lower = result['title'].lower()
            desc_lower = result['description'].lower()
            
            # Exact title match boost
            title_boost = 0.0
            if any(word in title_lower for word in query_lower.split() if len(word) > 2):
                title_boost = 0.1
            
            # Brand/category match boost
            brand_boost = 0.0
            if result['brand'].lower() in query_lower:
                brand_boost = 0.05
            
            category_boost = 0.0
            if result['category'].lower() in query_lower:
                category_boost = 0.05
            
            # Calculate final score
            base_score = sum(score_breakdown.values())
            final_score = (base_score + title_boost + brand_boost + category_boost) * availability_multiplier
            
            if include_breakdown:
                score_breakdown.update({
                    'title_match': title_boost,
                    'brand_match': brand_boost,
                    'category_match': category_boost,
                    'availability_penalty': 1.0 - availability_multiplier
                })
            
            # Create SearchResult
            search_result = SearchResult(
                product_id=result['product_id'],
                title=result['title'],
                description=result['description'],
                category=result['category'],
                brand=result['brand'],
                price=result['price'],
                rating=result['rating'],
                num_reviews=result['num_reviews'],
                availability=result['availability'],
                tags=result['tags'],
                specifications=result['specifications'],
                semantic_score=semantic_score,
                final_score=final_score,
                score_breakdown=score_breakdown if include_breakdown else {}
            )
            
            scored_results.append(search_result)
        
        return scored_results
    
    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get search query suggestions based on partial input."""
        suggestions = []
        
        # Add sample queries that match the partial input
        for sample in demo_config.sample_queries:
            if partial_query.lower() in sample.lower():
                suggestions.append(sample)
                
        # Add category-based suggestions
        for category in demo_config.categories:
            if partial_query.lower() in category.lower():
                suggestions.append(f"products in {category}")
        
        return suggestions[:limit]
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get available filter options for the UI."""
        return {
            'categories': demo_config.categories,
            'price_ranges': list(search_config.price_ranges.keys()),
            'availability_options': ['In Stock', 'Limited Stock', 'Out of Stock'],
            'rating_minimums': [3.0, 3.5, 4.0, 4.5, 5.0]
        }

# Global search engine instance
search_engine = None

def get_search_engine() -> SearchEngine:
    """Get or create the global search engine instance."""
    global search_engine
    if search_engine is None:
        search_engine = SearchEngine()
    return search_engine
