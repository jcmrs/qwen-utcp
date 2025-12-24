# UTCP Knowledge Base Integration Guide

## Overview
This guide provides instructions for integrating the UTCP Knowledge Base into other projects and making it accessible to AI assistants. The knowledge base contains comprehensive information extracted from 17 UTCP repositories, processed and optimized for AI consumption.

## Contents of the Knowledge Base

The UTCP Knowledge Base contains:
- **25,371 concepts** - Extracted from UTCP repositories
- **199,158 relationships** - Connections between concepts
- **870 principles** - Cross-repository principles
- **2 patterns** - Identified patterns in UTCP implementations

## Integration Methods

### Method 1: Direct File Access
The simplest method is to directly access the JSON files in the knowledge base.

#### Python Integration
```python
import json
from pathlib import Path

# Load the knowledge base
kb_path = Path("utcp-kb")  # Path to your knowledge base

# Load concepts
with open(kb_path / "processed-knowledge" / "all_concepts.json", 'r', encoding='utf-8') as f:
    concepts = json.load(f)

# Load relationships
with open(kb_path / "processed-knowledge" / "all_relationships.json", 'r', encoding='utf-8') as f:
    relationships = json.load(f)

# Load principles
with open(kb_path / "wisdom" / "principles" / "all_principles.json", 'r', encoding='utf-8') as f:
    principles = json.load(f)

print(f"Loaded {len(concepts)} concepts, {len(relationships)} relationships, {len(principles)} principles")
```

#### Using the Provided Loader
The knowledge base package includes a convenient loader script:

```python
from loader import UTCPKnowledgeBase

# Initialize the knowledge base
kb = UTCPKnowledgeBase("utcp-kb")

# Get all concepts
concepts = kb.get_concepts()

# Get all relationships
relationships = kb.get_relationships()

# Search for specific terms
utcp_concepts = kb.search_concepts("utcp")

# Get concepts from a specific repository
python_utcp_concepts = kb.get_concepts_by_repo("python-utcp")
```

### Method 2: API Access
For projects requiring programmatic access, the knowledge base includes a Flask-based API server.

#### Starting the API Server
```bash
# Install Flask if not already installed
pip install flask

# Start the API server
python utcp_kb_api.py --host 0.0.0.0 --port 8000
```

#### API Endpoints
- `GET /health` - Health check
- `GET /concepts` - Get all concepts
- `GET /concepts?repo=repo_name` - Get concepts from specific repository
- `GET /concepts?type=concept_type` - Get concepts of specific type
- `GET /relationships` - Get all relationships
- `GET /relationships?type=rel_type` - Get relationships of specific type
- `GET /principles` - Get all principles
- `GET /patterns` - Get all patterns
- `GET /search?q=query` - Global search across all knowledge
- `GET /search/concepts?q=query` - Search in concepts only
- `GET /repositories` - Get list of repositories
- `GET /stats` - Get statistics about the knowledge base

#### API Usage Examples
```python
import requests

# Base URL of the API server
BASE_URL = "http://localhost:8000"

# Search for UTCP-related concepts
response = requests.get(f"{BASE_URL}/search?q=utcp")
results = response.json()
print(f"Found {len(results['concepts'])} concepts related to 'utcp'")

# Get concepts from python-utcp repository
response = requests.get(f"{BASE_URL}/concepts?repo=python-utcp")
python_concepts = response.json()
print(f"Found {len(python_concepts)} concepts in python-utcp repository")

# Get statistics
response = requests.get(f"{BASE_URL}/stats")
stats = response.json()
print(f"Knowledge base contains {stats['total_concepts']} concepts")
```

### Method 3: Package Integration
If you have the packaged version of the knowledge base:

1. Extract the zip file to your project directory
2. The knowledge base will be in the `utcp-kb` subdirectory
3. Use either direct file access or API access as described above

## AI Assistant Integration Examples

### ChatGPT/Assistant Integration
Here's an example of how to integrate the knowledge base with an AI assistant:

```python
from loader import UTCPKnowledgeBase

class UTCPKnowledgeAssistant:
    def __init__(self, kb_path="utcp-kb"):
        self.kb = UTCPKnowledgeBase(kb_path)
    
    def answer_question(self, question):
        # Extract keywords from the question
        keywords = self.extract_keywords(question)
        
        # Search the knowledge base
        results = []
        for keyword in keywords:
            results.extend(self.kb.search_concepts(keyword))
        
        # Remove duplicates while preserving order
        unique_results = []
        seen = set()
        for result in results:
            if result['name'] not in seen:
                seen.add(result['name'])
                unique_results.append(result)
        
        # Format results for the AI
        context = self.format_context(unique_results[:5])  # Limit to 5 results
        return context
    
    def extract_keywords(self, text):
        # Simple keyword extraction - in practice, use NLP techniques
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        # Return common UTCP-related terms
        utcp_terms = [w for w in words if 'utcp' in w or 'tool' in w or 'protocol' in w]
        return utcp_terms or words[:3]  # Fallback to first 3 words
    
    def format_context(self, concepts):
        context = "UTCP Knowledge Base Results:\\n"
        for concept in concepts:
            context += f"- {concept['name']}: {concept['description']} (from {concept['source_repo']})\\n"
        return context

# Usage
assistant = UTCPKnowledgeAssistant()
question = "What is UTCP?"
context = assistant.answer_question(question)
print(context)
```

### Embedding Integration
For more advanced integration, you can use the embeddings provided in the knowledge base:

```python
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def load_embeddings(kb_path="utcp-kb"):
    """Load embeddings for semantic similarity search"""
    with open(f"{kb_path}/ai-optimized/embeddings/concept_embeddings.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # For this example, we use a simple hash-based embedding
    # In a real implementation, you would use proper vector embeddings
    embeddings = np.array([[int(c, 16) % 1000 for c in emb[:4]] for emb in data['embeddings']])
    return embeddings, data['metadata']

def find_similar_concepts(query, embeddings, metadata, top_k=5):
    """Find concepts similar to the query"""
    # This is a simplified example
    # In practice, you would use proper embedding models
    pass
```

## Deployment Considerations

### Local Deployment
- The knowledge base can be deployed locally with minimal dependencies
- For API access, Flask is required: `pip install flask`
- For advanced features: `pip install numpy scikit-learn`

### Server Deployment
- The API server can be deployed on any server that supports Python
- For production use, consider using a WSGI server like Gunicorn
- Example deployment command: `gunicorn -w 4 -b 0.0.0.0:8000 utcp_kb_api:app`

### Container Deployment
- The knowledge base can be containerized using Docker
- The entire knowledge base is self-contained and portable

## Best Practices

### For AI Assistants
1. **Caching**: Cache frequently accessed concepts to improve performance
2. **Context Limiting**: Limit the amount of context provided to avoid token limits
3. **Relevance Scoring**: Implement relevance scoring for search results
4. **Incremental Updates**: Plan for updates to the knowledge base

### For Integration
1. **Error Handling**: Always include error handling when accessing the knowledge base
2. **Performance**: Consider loading only the portions of the knowledge base you need
3. **Versioning**: Track the version of the knowledge base you're using
4. **Monitoring**: Monitor access patterns to optimize performance

## Troubleshooting

### Common Issues
1. **File Not Found**: Ensure the knowledge base path is correct
2. **Memory Issues**: For large knowledge bases, consider loading in chunks
3. **API Server Hanging**: Ensure Flask is installed and the port is available

### Performance Tips
1. **Indexing**: Use the provided indexes for faster search
2. **Filtering**: Filter results on the server side when possible
3. **Compression**: The knowledge base files are JSON and can be compressed

## License
The UTCP Knowledge Base is provided under the same license terms as the original UTCP repositories from which it was extracted. Please refer to the individual repositories for specific license information.

## Support
For issues with the knowledge base integration, please check:
- The `metadata.json` file for version and extraction information
- The original UTCP repositories for protocol-specific information
- This documentation for integration guidance