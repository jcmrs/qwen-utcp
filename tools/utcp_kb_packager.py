#!/usr/bin/env python3
"""
UTCP Knowledge Base Packager
Creates a portable distribution package of the knowledge base
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import subprocess


def create_knowledge_package(output_dir: str = "dist", package_name: str = "utcp-knowledge-base"):
    """Create a portable package of the knowledge base"""
    
    # Create distribution directory
    dist_path = Path(output_dir)
    dist_path.mkdir(exist_ok=True)
    
    # Create temporary directory for packaging
    temp_dir = dist_path / f"{package_name}_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating knowledge package in {temp_dir}")
    
    # Copy the knowledge base
    kb_source = Path(".utcp-kb")
    kb_dest = temp_dir / "utcp-kb"
    shutil.copytree(kb_source, kb_dest, dirs_exist_ok=True)
    
    # Create metadata
    metadata = {
        'package_name': package_name,
        'version': '1.0.0',
        'created_at': datetime.now().isoformat(),
        'kb_summary': get_kb_summary(),
        'source_repositories': get_source_repos(),
        'extraction_info': get_extraction_info(),
        'dependencies': [
            'python>=3.8',
            'json',
            'pathlib',
            'typing'
        ],
        'recommended_dependencies': [
            'flask>=2.0.0',  # For API access
            'numpy',          # For embedding operations
            'scikit-learn'    # For similarity search
        ]
    }
    
    metadata_path = temp_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # Create usage documentation
    create_usage_docs(temp_dir)
    
    # Create a simple loader script
    create_loader_script(temp_dir)
    
    # Create requirements file
    create_requirements_file(temp_dir)
    
    # Package as zip file
    zip_path = dist_path / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(temp_dir)
                zipf.write(file_path, arc_path)
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    print(f"Knowledge package created: {zip_path}")
    print(f"Package size: {zip_path.stat().st_size / (1024*1024):.2f} MB")
    
    return str(zip_path)


def get_kb_summary():
    """Get summary information about the knowledge base"""
    kb_path = Path(".utcp-kb")
    
    summary = {
        'total_concepts': 0,
        'total_relationships': 0,
        'total_principles': 0,
        'total_patterns': 0,
        'repositories_processed': 0,
        'extraction_date': None
    }
    
    # Get concept count
    concepts_path = kb_path / "processed-knowledge" / "all_concepts.json"
    if concepts_path.exists():
        with open(concepts_path, 'r', encoding='utf-8') as f:
            concepts = json.load(f)
        summary['total_concepts'] = len(concepts)
    
    # Get relationship count
    relationships_path = kb_path / "processed-knowledge" / "all_relationships.json"
    if relationships_path.exists():
        with open(relationships_path, 'r', encoding='utf-8') as f:
            relationships = json.load(f)
        summary['total_relationships'] = len(relationships)
    
    # Get principles count
    principles_path = kb_path / "wisdom" / "principles" / "all_principles.json"
    if principles_path.exists():
        with open(principles_path, 'r', encoding='utf-8') as f:
            principles = json.load(f)
        summary['total_principles'] = len(principles)
    
    # Get patterns count
    patterns_path = kb_path / "wisdom" / "patterns" / "all_patterns.json"
    if patterns_path.exists():
        with open(patterns_path, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
        summary['total_patterns'] = len(patterns)
    
    # Count repositories processed
    raw_extractions_path = kb_path / "raw-extractions"
    if raw_extractions_path.exists():
        repos = [d for d in raw_extractions_path.iterdir() if d.is_dir()]
        summary['repositories_processed'] = len(repos)
    
    return summary


def get_source_repos():
    """Get information about source repositories"""
    repos = []
    raw_extractions_path = Path(".utcp-kb") / "raw-extractions"
    
    if raw_extractions_path.exists():
        for repo_dir in raw_extractions_path.iterdir():
            if repo_dir.is_dir():
                # Look for extraction files to get commit info
                extraction_files = list(repo_dir.glob("extraction_*.json"))
                if extraction_files:
                    with open(extraction_files[0], 'r', encoding='utf-8') as f:
                        extraction = json.load(f)
                    repos.append({
                        'name': extraction.get('repository', repo_dir.name),
                        'commit_hash': extraction.get('commit_hash', 'unknown'),
                        'file_count': extraction.get('file_count', 0),
                        'extraction_timestamp': extraction.get('timestamp', 'unknown')
                    })
    
    return repos


def get_extraction_info():
    """Get information about the extraction process"""
    config_path = Path(".utcp-kb") / "config" / "extraction_config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return {
            'config_used': config,
            'extraction_timestamp': datetime.now().isoformat()
        }
    return {}


def create_usage_docs(output_dir):
    """Create usage documentation for the knowledge base"""
    docs_content = """
# UTCP Knowledge Base Usage Guide

## Overview
This package contains a comprehensive knowledge base extracted from UTCP repositories, optimized for AI assistant consumption.

## Contents
- `utcp-kb/` - The main knowledge base directory
- `metadata.json` - Information about the knowledge base
- `loader.py` - Simple loader script for integration
- `requirements.txt` - Dependencies for advanced features

## Integration

### Basic Integration
```python
import json
from pathlib import Path

# Load the knowledge base
kb_path = Path("utcp-kb")
concepts_path = kb_path / "processed-knowledge" / "all_concepts.json"

with open(concepts_path, 'r', encoding='utf-8') as f:
    concepts = json.load(f)

print(f"Loaded {len(concepts)} concepts")
```

### Using the Loader Script
```python
from loader import UTCPKnowledgeBase

kb = UTCPKnowledgeBase("utcp-kb")
concepts = kb.get_concepts()
relationships = kb.get_relationships()
principles = kb.get_principles()
```

## Knowledge Structure

### Concepts
- `name`: The name of the concept
- `type`: The type of concept (title, term, path_component)
- `source_repo`: The repository where the concept was found
- `description`: A brief description of the concept

### Relationships
- `source`: The source concept
- `target`: The target concept
- `type`: The type of relationship (co_occurrence, contains)
- `strength`: A measure of relationship strength
- `context`: The context where the relationship was found

### Wisdom Components
- Principles: Core principles identified across repositories
- Patterns: Common patterns in UTCP implementations

## API Access
For programmatic access, you can use the provided API server:
```bash
python -m pip install flask
python api_server.py
```

Then query the API endpoints:
- GET /concepts
- GET /relationships
- GET /wisdom
- GET /search?q=term

## License
This knowledge base is provided under the same license as the source UTCP repositories.
"""
    
    docs_path = Path(output_dir) / "USAGE.md"
    with open(docs_path, 'w', encoding='utf-8') as f:
        f.write(docs_content)


def create_loader_script(output_dir):
    """Create a simple loader script for easy integration"""
    loader_content = '''
"""
UTCP Knowledge Base Loader
Simple interface for loading and accessing the knowledge base
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class UTCPKnowledgeBase:
    """Simple interface for accessing the UTCP knowledge base"""
    
    def __init__(self, kb_path: str = "utcp-kb"):
        """Initialize with path to knowledge base directory"""
        self.kb_path = Path(kb_path)
        self._concepts = None
        self._relationships = None
        self._principles = None
        self._patterns = None
    
    def _load_json(self, subpath: str) -> Any:
        """Load a JSON file from the knowledge base"""
        file_path = self.kb_path / subpath
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def get_concepts(self) -> List[Dict[str, Any]]:
        """Get all concepts"""
        if self._concepts is None:
            self._concepts = self._load_json("processed-knowledge/all_concepts.json")
        return self._concepts
    
    def get_relationships(self) -> List[Dict[str, Any]]:
        """Get all relationships"""
        if self._relationships is None:
            self._relationships = self._load_json("processed-knowledge/all_relationships.json")
        return self._relationships
    
    def get_principles(self) -> List[Dict[str, Any]]:
        """Get all principles"""
        if self._principles is None:
            self._principles = self._load_json("wisdom/principles/all_principles.json")
        return self._principles
    
    def get_patterns(self) -> List[Dict[str, Any]]:
        """Get all patterns"""
        if self._patterns is None:
            self._patterns = self._load_json("wisdom/patterns/all_patterns.json")
        return self._patterns
    
    def search_concepts(self, query: str) -> List[Dict[str, Any]]:
        """Simple search in concepts by name or description"""
        query_lower = query.lower()
        concepts = self.get_concepts()
        results = []
        
        for concept in concepts:
            if (query_lower in concept.get('name', '').lower() or 
                query_lower in concept.get('description', '').lower() or
                query_lower in concept.get('context', '').lower()):
                results.append(concept)
        
        return results
    
    def get_concepts_by_repo(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get concepts from a specific repository"""
        concepts = self.get_concepts()
        return [c for c in concepts if c.get('source_repo') == repo_name]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the knowledge base if available"""
        metadata_path = self.kb_path / ".." / "metadata.json"  # Look in parent if in dist
        if not metadata_path.exists():
            metadata_path = Path("metadata.json")  # Try current directory
        
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


# Example usage
if __name__ == "__main__":
    kb = UTCPKnowledgeBase()
    
    print(f"Knowledge base loaded:")
    print(f"- {len(kb.get_concepts())} concepts")
    print(f"- {len(kb.get_relationships())} relationships")
    print(f"- {len(kb.get_principles())} principles")
    print(f"- {len(kb.get_patterns())} patterns")
    
    # Example search
    results = kb.search_concepts("utcp")
    print(f"\\nFound {len(results)} concepts related to 'utcp'")
    for r in results[:5]:  # Show first 5
        print(f"- {r['name']} ({r['source_repo']})")
'''
    
    loader_path = Path(output_dir) / "loader.py"
    with open(loader_path, 'w', encoding='utf-8') as f:
        f.write(loader_content)


def create_requirements_file(output_dir):
    """Create a requirements file for dependencies"""
    requirements_content = """# UTCP Knowledge Base Requirements

# Core requirements (for basic functionality)
python>=3.8

# For API access
flask>=2.0.0

# For advanced similarity search (optional)
numpy
scikit-learn

# For enhanced NLP (optional)
spacy>=3.4.0
sentence-transformers>=2.2.0
"""
    
    req_path = Path(output_dir) / "requirements.txt"
    with open(req_path, 'w', encoding='utf-8') as f:
        f.write(requirements_content)


def main():
    """Main function to create the knowledge package"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create a portable UTCP knowledge base package")
    parser.add_argument("--output-dir", default="dist", help="Output directory for the package")
    parser.add_argument("--package-name", default="utcp-knowledge-base", help="Name of the package")
    
    args = parser.parse_args()
    
    package_path = create_knowledge_package(args.output_dir, args.package_name)
    print(f"Package created successfully: {package_path}")


if __name__ == "__main__":
    main()