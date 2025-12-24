#!/usr/bin/env python3
"""
Basic UTCP AI Optimizer
Simple implementation without external AI dependencies
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime
from collections import defaultdict
import hashlib


def load_processed_knowledge(processed_dir: Path) -> tuple:
    """Load processed knowledge components"""
    concepts_path = processed_dir / "all_concepts.json"
    relationships_path = processed_dir / "all_relationships.json"
    
    concepts = []
    relationships = []
    
    if concepts_path.exists():
        with open(concepts_path, 'r', encoding='utf-8') as f:
            concepts = json.load(f)
    
    if relationships_path.exists():
        with open(relationships_path, 'r', encoding='utf-8') as f:
            relationships = json.load(f)
    
    return concepts, relationships


def generate_basic_embeddings(texts: List[str]) -> List[str]:
    """Generate basic 'embeddings' using simple hash-based approach"""
    # This is a very basic approach - in a real system, we'd use proper vectorization
    embeddings = []
    for text in texts:
        # Create a simple hash-based representation
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        embeddings.append(text_hash)
    return embeddings


def create_search_index(concepts: List[Dict], relationships: List[Dict], output_dir: Path):
    """Create a basic search index"""
    # Create a simple inverted index for concepts
    concept_index = defaultdict(list)
    for i, concept in enumerate(concepts):
        # Index by name and description
        name = concept['name'].lower()
        description = concept.get('description', '').lower()
        
        # Add to index
        words = (name + ' ' + description).split()
        for word in words:
            if len(word) > 2:  # Only index words longer than 2 characters
                concept_index[word].append(i)
    
    # Create a simple inverted index for relationships
    relationship_index = defaultdict(list)
    for i, relationship in enumerate(relationships):
        # Index by source, target, and context
        source = relationship['source'].lower()
        target = relationship['target'].lower()
        context = relationship.get('context', '').lower()
        
        # Add to index
        words = (source + ' ' + target + ' ' + context).split()
        for word in words:
            if len(word) > 2:
                relationship_index[word].append(i)
    
    # Save indexes
    index_dir = output_dir / "indexes"
    index_dir.mkdir(parents=True, exist_ok=True)
    
    with open(index_dir / "concept_index.json", 'w', encoding='utf-8') as f:
        # Convert defaultdict to regular dict for JSON serialization
        concept_index_dict = {k: v for k, v in concept_index.items()}
        json.dump(concept_index_dict, f, indent=2)
    
    with open(index_dir / "relationship_index.json", 'w', encoding='utf-8') as f:
        # Convert defaultdict to regular dict for JSON serialization
        relationship_index_dict = {k: v for k, v in relationship_index.items()}
        json.dump(relationship_index_dict, f, indent=2)


def create_basic_summaries(concepts: List[Dict], relationships: List[Dict], output_dir: Path):
    """Create basic summaries optimized for simple AI consumption"""
    # Create a comprehensive summary
    summary_data = {
        'kb_overview': {
            'total_concepts': len(concepts),
            'total_relationships': len(relationships),
            'timestamp': datetime.now().isoformat()
        },
        'concept_types': {},
        'relationship_types': {},
        'repositories_mentioned': set(),
        'key_terms': []
    }
    
    # Count concept types
    for concept in concepts:
        concept_type = concept['type']
        if concept_type not in summary_data['concept_types']:
            summary_data['concept_types'][concept_type] = 0
        summary_data['concept_types'][concept_type] += 1
        
        # Track repositories
        summary_data['repositories_mentioned'].add(concept['source_repo'])
    
    # Count relationship types
    for relationship in relationships:
        rel_type = relationship['type']
        if rel_type not in summary_data['relationship_types']:
            summary_data['relationship_types'][rel_type] = 0
        summary_data['relationship_types'][rel_type] += 1
        
        # Track repositories
        summary_data['repositories_mentioned'].add(relationship['source_repo'])
    
    # Convert set to list for JSON serialization
    summary_data['repositories_mentioned'] = list(summary_data['repositories_mentioned'])
    
    # Extract key terms (top occurring terms)
    term_counts = defaultdict(int)
    for concept in concepts:
        term_counts[concept['name']] += 1
    
    summary_data['key_terms'] = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:50]
    
    # Save summary
    summary_dir = output_dir / "summaries"
    summary_dir.mkdir(parents=True, exist_ok=True)
    
    summary_path = summary_dir / "comprehensive_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, default=str)


def create_basic_embeddings_storage(concepts: List[Dict], relationships: List[Dict], output_dir: Path):
    """Create basic storage for embeddings"""
    # Prepare text data for basic "embedding"
    concept_texts = []
    for concept in concepts:
        text = f"{concept['name']} {concept['description']} {concept['context']}".lower()
        concept_texts.append(text)
    
    relationship_texts = []
    for relationship in relationships:
        text = f"{relationship['source']} {relationship['type']} {relationship['target']} {relationship['context']}".lower()
        relationship_texts.append(text)
    
    # Generate basic embeddings
    concept_embeddings = generate_basic_embeddings(concept_texts)
    relationship_embeddings = generate_basic_embeddings(relationship_texts)
    
    # Save embeddings
    embeddings_dir = output_dir / "embeddings"
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    # Save concept embeddings
    with open(embeddings_dir / "concept_embeddings.json", 'w', encoding='utf-8') as f:
        json.dump({
            'embeddings': concept_embeddings,
            'metadata': [{'id': i, 'name': concepts[i]['name']} for i in range(len(concepts))]
        }, f, indent=2)
    
    # Save relationship embeddings
    with open(embeddings_dir / "relationship_embeddings.json", 'w', encoding='utf-8') as f:
        json.dump({
            'embeddings': relationship_embeddings,
            'metadata': [{'id': i, 'source': relationships[i]['source'], 'target': relationships[i]['target']} for i in range(len(relationships))]
        }, f, indent=2)


def main():
    """Main function for basic AI optimization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Basic UTCP AI Optimizer")
    parser.add_argument("--input-dir", default=".utcp-kb/processed-knowledge", 
                       help="Input directory containing processed knowledge")
    parser.add_argument("--output-dir", default=".utcp-kb/ai-optimized", 
                       help="Output directory for AI-optimized knowledge")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    print("Loading processed knowledge...")
    concepts, relationships = load_processed_knowledge(input_path)
    
    print(f"Loaded {len(concepts)} concepts and {len(relationships)} relationships")
    
    # Create search indexes
    print("Creating search indexes...")
    create_search_index(concepts, relationships, output_path)
    
    # Create basic embeddings
    print("Creating basic embeddings...")
    create_basic_embeddings_storage(concepts, relationships, output_path)
    
    # Create summaries
    print("Creating AI-optimized summaries...")
    create_basic_summaries(concepts, relationships, output_path)
    
    print("Basic AI optimization completed!")


if __name__ == "__main__":
    main()