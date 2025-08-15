# Qdrant Semantic E-commerce Search Demo

## Project Overview
This project demonstrates **Project #4: Semantic Search on Structured and Unstructured Data** using Qdrant vector database. It combines semantic search on product descriptions with structured filtering on product metadata.

## Features
- 🔍 **Hybrid Search**: Semantic similarity + structured filtering
- 📊 **Rich Metadata**: Price, category, brand, ratings, availability
- 🎯 **Custom Scoring**: Business logic combining relevance signals
- 🌐 **Web Interface**: Interactive demo for presentations
- 📈 **Visual Results**: Clear comparison of search approaches

## Architecture
```
User Query → Embedding Model → Qdrant Vector Search → Custom Scoring → Ranked Results
               ↓
           Structured Filters (price, category, etc.)
```

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
./start_demo.sh
streamlit run demo_app.py
```

### Option 2: Manual Setup

1. **Verify Prerequisites**
   ```bash
   python verify_setup.py
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
   python setup_data.py
   ```

5. **Launch Demo**
   ```bash
   streamlit run demo_app.py
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
