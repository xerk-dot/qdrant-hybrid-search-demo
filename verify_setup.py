"""Verification script to test the demo setup."""

import sys
import importlib
import traceback

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    required_modules = [
        'qdrant_client',
        'sentence_transformers', 
        'streamlit',
        'pandas',
        'plotly',
        'numpy'
    ]
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            return False
    
    return True

def test_local_modules():
    """Test that our custom modules can be imported."""
    print("\n🏠 Testing local modules...")
    
    local_modules = [
        'config',
        'data_generator', 
        'embedding_service',
        'qdrant_manager',
        'search_engine'
    ]
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            return False
    
    return True

def test_data_generation():
    """Test data generation functionality."""
    print("\n📊 Testing data generation...")
    
    try:
        from data_generator import EcommerceDataGenerator
        
        generator = EcommerceDataGenerator()
        products = generator.generate_products(10)  # Small test
        
        if len(products) == 10:
            print("  ✅ Data generation working")
            print(f"  📝 Sample product: {products[0].title}")
            return True
        else:
            print(f"  ❌ Expected 10 products, got {len(products)}")
            return False
            
    except Exception as e:
        print(f"  ❌ Data generation failed: {e}")
        traceback.print_exc()
        return False

def test_embeddings():
    """Test embedding service."""
    print("\n🧠 Testing embedding service...")
    
    try:
        from embedding_service import get_embedding_service
        
        service = get_embedding_service()
        
        # Test query encoding
        embedding = service.encode_query("test product")
        
        if len(embedding) == 384:  # Expected dimension
            print("  ✅ Embedding service working")
            print(f"  📏 Embedding dimension: {len(embedding)}")
            return True
        else:
            print(f"  ❌ Wrong embedding dimension: {len(embedding)}")
            return False
            
    except Exception as e:
        print(f"  ❌ Embedding service failed: {e}")
        traceback.print_exc()
        return False

def test_qdrant_connection():
    """Test Qdrant connection (requires Qdrant to be running)."""
    print("\n🗄️ Testing Qdrant connection...")
    
    try:
        from qdrant_manager import QdrantManager
        
        manager = QdrantManager()
        
        # Try to connect (this will fail if Qdrant is not running)
        collections = manager.client.get_collections()
        print("  ✅ Qdrant connection successful")
        print(f"  📋 Found {len(collections.collections)} collections")
        return True
        
    except Exception as e:
        print(f"  ⚠️ Qdrant connection failed: {e}")
        print("  💡 Make sure Qdrant is running: docker-compose up -d qdrant")
        return False

def main():
    """Run all verification tests."""
    print("🔧 Qdrant Demo Setup Verification")
    print("=" * 40)
    
    tests = [
        ("Package imports", test_imports),
        ("Local modules", test_local_modules), 
        ("Data generation", test_data_generation),
        ("Embedding service", test_embeddings),
        ("Qdrant connection", test_qdrant_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Demo is ready to run.")
        print("\nNext steps:")
        print("1. Start Qdrant: docker-compose up -d qdrant")
        print("2. Setup data: python setup_data.py")
        print("3. Run demo: streamlit run demo_app.py")
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed. Please fix issues before proceeding.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
