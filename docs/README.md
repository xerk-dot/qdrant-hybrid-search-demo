# Qdrant E-commerce Search Demo
## Semantic Search on Structured and Unstructured Data

**Demonstrate hybrid search combining semantic similarity with structured filtering using Qdrant vector database.**

## 🚀 Features
- 🔍 **Hybrid Search**: Semantic similarity + structured filtering
- 📊 **Rich Metadata**: Price, category, brand, ratings, availability
- 🎯 **Custom Scoring**: Business logic combining relevance signals
- 🌐 **Web Interface**: Interactive demo for presentations
- 📈 **Visual Results**: Clear comparison of search approaches

## 📁 Project Structure

```
qdrant_interview/
├── 📂 src/                    # Core application code
│   ├── core/                  # Core business logic
│   │   ├── config.py          # Configuration settings
│   │   ├── embedding_service.py # Sentence transformer embeddings
│   │   ├── qdrant_manager.py   # Qdrant client and collection management
│   │   └── search_engine.py    # Hybrid search logic
│   ├── data/                  # Data generation and management
│   │   ├── data_generator.py   # Sample e-commerce data generation
│   │   └── setup_data.py       # Database initialization
│   └── ui/                    # User interface
│       └── demo_app.py         # Streamlit web interface
├── 📂 scripts/               # Utility scripts
│   ├── start_demo.sh          # Automated setup script
│   └── verify_setup.py        # Prerequisites verification
├── 📂 docs/                  # Documentation
│   ├── presentation/
│   │   ├── presentation_notes.md  # Detailed presentation guide
│   │   └── presentation_slides.md # Slide templates
│   ├── README.md              # This file
│   └── PROJECT_SUMMARY.md     # Complete project overview
├── 📂 data/                  # Generated data (gitignored)
│   └── products.json          # Sample products
├── docker-compose.yml         # Qdrant container setup
└── requirements.txt           # Python dependencies
```

## 🏗️ Architecture
```
User Query → Embedding Model → Qdrant Vector Search → Custom Scoring → Ranked Results
               ↓
           Structured Filters (price, category, etc.)
```

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
./scripts/start_demo.sh
python3 -m streamlit run src/ui/demo_app.py
```

### Option 2: Manual Setup

1. **Verify Prerequisites**
   ```bash
   python3 scripts/verify_setup.py
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Qdrant**
   ```bash
   docker-compose up -d qdrant
   ```

4. **Setup Demo Data**
   ```bash
   python3 src/data/setup_data.py
   ```

5. **Launch Demo**
   ```bash
   python3 -m streamlit run src/ui/demo_app.py
   ```

6. **Open Browser**
   - Navigate to: http://localhost:8501

## Demo Scenarios
- **Semantic Query**: "comfortable running shoes" → finds athletic footwear
- **Hybrid Search**: "gaming laptop under $1000" → semantic + price filter
- **Category + Semantic**: "wireless headphones for travel" → category + description match

## Presentation Points
1. **Problem**: Traditional keyword search misses semantic meaning
2. **Solution**: Vector embeddings + structured metadata in Qdrant
3. **Demo**: Live search showing improved relevance
4. **Technical**: Payload indexing and custom scoring explained

## Database Size

**Current Demo Dataset:**
- **Products**: 1,000 e-commerce items
- **Vector Data**: ~1.5 MB (384-dim embeddings)
- **Metadata**: ~1 MB (structured product data)
- **Total Size**: ~4-5 MB with HNSW index

**Scaling Potential:**
- **1M products**: ~4-5 GB
- **10M products**: ~40-50 GB
- **Optimizations**: Quantization can reduce by 4-32x

## Technical Stack
- **Vector Database**: Qdrant for similarity search and filtering
- **Embeddings**: all-MiniLM-L6-v2 sentence transformer (384 dimensions)
- **UI**: Streamlit with interactive visualizations
- **Backend**: Python with custom hybrid search logic
- **Deployment**: Docker containerization
