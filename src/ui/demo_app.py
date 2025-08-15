"""Streamlit demo application for Qdrant e-commerce search."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import logging
import json
from src.core.search_engine import get_search_engine, SearchResult
from src.core.config import demo_config, search_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=demo_config.app_title,
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def initialize_search_engine():
    """Initialize and cache the search engine."""
    return get_search_engine()

# Session state for search query
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

def format_price(price: float) -> str:
    """Format price for display."""
    return f"${price:,.2f}"

def format_rating(rating: float) -> str:
    """Format rating with stars."""
    stars = "⭐" * int(rating)
    return f"{rating} {stars}"

def display_search_result(result: SearchResult, show_scoring: bool = False):
    """Display a single search result."""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.subheader(result.title)
            st.write(f"**Category:** {result.category} | **Brand:** {result.brand}")
            st.write(result.description)
            
            # Tags
            if result.tags:
                tag_str = " ".join([f"`{tag}`" for tag in result.tags[:5]])
                st.markdown(f"**Tags:** {tag_str}")
        
        with col2:
            st.metric("Price", format_price(result.price))
            st.metric("Rating", format_rating(result.rating), f"{result.num_reviews} reviews")
        
        with col3:
            # Availability badge
            if result.availability == "In Stock":
                st.success(f"✅ {result.availability}")
            elif result.availability == "Limited Stock":
                st.warning(f"⚠️ {result.availability}")
            else:
                st.error(f"❌ {result.availability}")
            
            # Semantic score
            st.metric("Relevance", f"{result.semantic_score:.3f}")
        
        # Show scoring breakdown if requested
        if show_scoring and result.score_breakdown:
            with st.expander("🔍 Scoring Details"):
                breakdown_df = pd.DataFrame([
                    {"Factor": k.replace("_", " ").title(), "Score": f"{v:.4f}"}
                    for k, v in result.score_breakdown.items()
                ])
                st.dataframe(breakdown_df, use_container_width=True)
        
        st.divider()

def create_results_visualization(results: List[SearchResult]):
    """Create visualizations for search results."""
    if not results:
        return
    
    # Create DataFrame for plotting
    df = pd.DataFrame([
        {
            "Title": result.title[:30] + "..." if len(result.title) > 30 else result.title,
            "Category": result.category,
            "Brand": result.brand,
            "Price": result.price,
            "Rating": result.rating,
            "Semantic Score": result.semantic_score,
            "Final Score": result.final_score,
            "Reviews": result.num_reviews
        }
        for result in results[:10]  # Top 10 for visualization
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score comparison
        fig_scores = go.Figure()
        fig_scores.add_trace(go.Bar(
            name='Semantic Score',
            x=df['Title'],
            y=df['Semantic Score'],
            marker_color='lightblue'
        ))
        fig_scores.add_trace(go.Bar(
            name='Final Score',
            x=df['Title'],
            y=df['Final Score'],
            marker_color='darkblue'
        ))
        
        fig_scores.update_layout(
            title="Semantic vs Final Scores",
            xaxis_title="Products",
            yaxis_title="Score",
            barmode='group',
            xaxis={'tickangle': 45}
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    
    with col2:
        # Price vs Rating scatter
        fig_scatter = px.scatter(
            df,
            x='Price',
            y='Rating',
            size='Reviews',
            color='Category',
            hover_data=['Brand', 'Semantic Score'],
            title="Price vs Rating (sized by reviews)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

def main():
    """Main application function."""
    
    # Header
    st.title("🔍 " + demo_config.app_title)
    st.markdown("""
    **Demonstrate hybrid search combining semantic similarity with structured filtering using Qdrant vector database.**
    
    This demo shows how to search across both unstructured text (product descriptions) and structured metadata 
    (price, category, brand, ratings) to provide more relevant results than traditional keyword search.
    """)
    
    # Initialize search engine
    try:
        search_engine = initialize_search_engine()
    except Exception as e:
        st.error(f"Failed to initialize search engine: {e}")
        st.stop()
    
    # Sidebar for filters
    st.sidebar.header("🏛️ Search Filters")
    
    # Get filter options
    filter_options = search_engine.get_filter_options()
    
    # Category filter
    selected_category = st.sidebar.selectbox(
        "Category",
        options=["All"] + filter_options['categories'],
        index=0
    )
    
    # Brand filter (simplified - you could make this dynamic based on data)
    brand_input = st.sidebar.text_input("Brand (optional)")
    
    # Price range
    price_range = st.sidebar.slider(
        "Price Range",
        min_value=0,
        max_value=2000,
        value=(0, 1000),
        step=50,
        format="$%d"
    )
    
    # Rating filter
    min_rating = st.sidebar.selectbox(
        "Minimum Rating",
        options=[0.0] + filter_options['rating_minimums'],
        index=0,
        format_func=lambda x: f"{x} stars" if x > 0 else "Any rating"
    )
    
    # Availability filter
    availability_filter = st.sidebar.selectbox(
        "Availability",
        options=["All"] + filter_options['availability_options'],
        index=0
    )
    
    # Advanced options
    with st.sidebar.expander("⚙️ Advanced Options"):
        show_scoring = st.checkbox("Show scoring breakdown", value=False)
        result_limit = st.slider("Max results", min_value=5, max_value=50, value=20)
    
    # Main search interface
    st.header("🔎 Search Products")
    
    # Sample queries
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Enter your search query:",
            value=st.session_state.search_query,
            placeholder="e.g., comfortable running shoes, gaming laptop under $1000, wireless headphones",
            help="Try natural language queries! The system understands price ranges, categories, and product features."
        )
    
    with col2:
        st.write("**Try these examples:**")
        for i, example in enumerate(demo_config.sample_queries[:4]):
            if st.button(example, key=f"example_{i}"):
                st.session_state.search_query = example
                st.rerun()
    
    # Build filters dictionary
    filters = {}
    if selected_category != "All":
        filters['category'] = selected_category
    if brand_input.strip():
        filters['brand'] = brand_input.strip()
    if price_range[0] > 0:
        filters['price_min'] = price_range[0]
    if price_range[1] < 2000:
        filters['price_max'] = price_range[1]
    if min_rating > 0:
        filters['rating_min'] = min_rating
    if availability_filter != "All":
        filters['availability'] = availability_filter
    
    # Perform search
    if search_query:
        with st.spinner("Searching products..."):
            try:
                results = search_engine.search(
                    query=search_query,
                    filters=filters,
                    limit=result_limit,
                    include_score_breakdown=show_scoring
                )
                
                if results:
                    st.success(f"Found {len(results)} relevant products")
                    
                    # Results summary
                    with st.expander("📊 Results Overview", expanded=False):
                        create_results_visualization(results)
                    
                    # Display results
                    st.header("🛍️ Search Results")
                    
                    for i, result in enumerate(results):
                        with st.container():
                            st.markdown(f"### {i+1}. Result")
                            display_search_result(result, show_scoring)
                
                else:
                    st.warning("No products found matching your criteria. Try adjusting your search query or filters.")
                    
            except Exception as e:
                st.error(f"Search failed: {e}")
                logger.exception("Search failed")
    
    # Information about the demo
    with st.expander("ℹ️ About this Demo"):
        st.markdown("""
        ### How it works:
        
        1. **Semantic Search**: Product descriptions are converted to vector embeddings using a sentence transformer model
        2. **Structured Filtering**: Metadata like price, category, and brand are indexed for efficient filtering
        3. **Hybrid Scoring**: Results combine semantic similarity with business logic (ratings, popularity, availability)
        4. **Query Understanding**: Natural language queries are parsed to extract implicit filters (e.g., "under $500")
        
        ### Technical Architecture:
        
        - **Vector Database**: Qdrant for similarity search and filtering
        - **Embeddings**: all-MiniLM-L6-v2 sentence transformer (384 dimensions)
        - **Hybrid Search**: Combines dense vectors with structured metadata
        - **Custom Scoring**: Weighted combination of semantic relevance, ratings, and popularity
        
        ### Demo Dataset:
        
        - **Products**: 1,000 synthetic e-commerce products
        - **Categories**: Electronics, Clothing, Sports & Outdoors, Home & Garden
        - **Metadata**: Price, brand, ratings, availability, specifications
        """)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        Built with Qdrant Vector Database | Streamlit | Sentence Transformers
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

