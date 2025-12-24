# UTCP Toolbelt Summary

## Directory Structure
```
tools/
├── basic_utcp_extractor.py     # Basic extraction tool
├── basic_utcp_processor.py     # Basic processing tool
├── basic_utcp_ai_optimizer.py  # Basic AI optimization tool
├── basic_utcp_system.py        # Main orchestration tool
├── basic_utcp_api.py          # Basic API for knowledge access
├── requirements.txt           # Dependencies for enhanced functionality
├── README.md                 # Documentation
└── __pycache__/              # Python cache (will be created at runtime)
```

## Tool Descriptions

### 1. basic_utcp_extractor.py
- Extracts content from UTCP repositories
- Identifies titles, summaries, and key terms
- Creates raw extraction files
- Works with minimal dependencies

### 2. basic_utcp_processor.py
- Processes raw extractions into structured knowledge
- Creates concepts and relationships
- Generates summaries
- Identifies potential principles and patterns

### 3. basic_utcp_ai_optimizer.py
- Creates basic search indexes
- Generates simple "embeddings" using hash functions
- Creates AI-optimized summaries
- Prepares knowledge for basic AI consumption

### 4. basic_utcp_system.py
- Orchestrates the full pipeline
- Supports extraction, processing, optimization
- Provides reporting capabilities
- Command-line interface

### 5. basic_utcp_api.py
- Provides HTTP API for knowledge access
- Supports search functionality
- No external web framework dependencies
- Built with Python standard library

## Usage Examples

### Full Pipeline
```bash
cd tools
python basic_utcp_system.py full
```

### Selective Extraction
```bash
python basic_utcp_system.py extract --repo python-utcp --repo typescript-utcp
```

### Run API
```bash
python basic_utcp_api.py --port 8000
```

Then access:
- Health check: http://localhost:8000/health
- All concepts: http://localhost:8000/concepts
- Search: http://localhost:8000/search?q=utcp