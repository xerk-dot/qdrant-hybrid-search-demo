"""Setup script to initialize the Qdrant database with sample e-commerce data."""

import json
import logging
from data_generator import EcommerceDataGenerator
from embedding_service import get_embedding_service
from qdrant_manager import QdrantManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main setup function to initialize the database."""
    
    print("🚀 Starting Qdrant E-commerce Search Demo Setup")
    print("=" * 50)
    
    # Step 1: Generate sample data
    print("\n📊 Generating sample e-commerce data...")
    generator = EcommerceDataGenerator()
    products = generator.generate_products(num_products=1000)
    
    # Save products to JSON for reference
    products_dict = []
    for product in products:
        product_dict = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "category": product.category,
            "brand": product.brand,
            "price": product.price,
            "rating": product.rating,
            "num_reviews": product.num_reviews,
            "availability": product.availability,
            "tags": product.tags,
            "specifications": product.specifications
        }
        products_dict.append(product_dict)
    
    with open('products.json', 'w') as f:
        json.dump(products_dict, f, indent=2)
    
    print(f"✅ Generated {len(products)} products and saved to products.json")
    
    # Step 2: Initialize embedding service
    print("\n🧠 Initializing embedding service...")
    embedding_service = get_embedding_service()
    model_info = embedding_service.get_model_info()
    print(f"✅ Loaded model: {model_info['model_name']}")
    print(f"   Embedding dimension: {model_info['embedding_dimension']}")
    
    # Step 3: Generate embeddings
    print("\n🔢 Generating embeddings for product descriptions...")
    embeddings = embedding_service.encode_products(products_dict)
    
    if not embeddings:
        print("❌ Failed to generate embeddings")
        return False
    
    print(f"✅ Generated {len(embeddings)} embeddings")
    
    # Step 4: Setup Qdrant collection
    print("\n🗄️ Setting up Qdrant collection...")
    qdrant_manager = QdrantManager()
    
    success = qdrant_manager.create_collection(recreate=True)
    if not success:
        print("❌ Failed to create Qdrant collection")
        return False
    
    print("✅ Qdrant collection created successfully")
    
    # Step 5: Insert data into Qdrant
    print("\n📤 Inserting products into Qdrant...")
    success = qdrant_manager.upsert_products(products_dict, embeddings)
    
    if not success:
        print("❌ Failed to insert products into Qdrant")
        return False
    
    print("✅ Products inserted successfully")
    
    # Step 6: Verify setup
    print("\n🔍 Verifying setup...")
    collection_info = qdrant_manager.get_collection_info()
    print(f"✅ Collection status: {collection_info.get('status', 'Unknown')}")
    print(f"   Points count: {collection_info.get('points_count', 0)}")
    print(f"   Vectors count: {collection_info.get('vectors_count', 0)}")
    
    # Step 7: Test search functionality
    print("\n🔎 Testing search functionality...")
    test_query = "comfortable running shoes"
    query_embedding = embedding_service.encode_query(test_query)
    
    if query_embedding:
        test_results = qdrant_manager.search_products(
            query_vector=query_embedding,
            limit=3
        )
        
        print(f"✅ Test search for '{test_query}' returned {len(test_results)} results")
        
        if test_results:
            print("\nTop result:")
            result = test_results[0]
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Category: {result.get('category', 'N/A')}")
            print(f"   Score: {result.get('score', 0):.3f}")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the demo: streamlit run demo_app.py")
    print("2. Open your browser to the displayed URL")
    print("3. Try searching for products!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Setup failed. Please check the logs above.")
            exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        logger.exception("Setup failed")
        exit(1)
