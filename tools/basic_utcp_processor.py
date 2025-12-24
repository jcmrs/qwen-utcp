#!/usr/bin/env python3
"""
Basic UTCP Knowledge Processor
Simple implementation without external dependencies beyond Python standard library
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime
from collections import defaultdict, Counter


def load_raw_extractions(extractions_dir: Path) -> List[Dict[str, Any]]:
    """Load all raw extractions from the specified directory"""
    extractions = []
    
    for repo_dir in extractions_dir.iterdir():
        if repo_dir.is_dir():
            # Process each extraction file in the repository directory
            for extraction_file in repo_dir.glob("extraction_*.json"):
                with open(extraction_file, 'r', encoding='utf-8') as f:
                    extraction_data = json.load(f)
                extractions.append(extraction_data)
    
    return extractions


def process_extraction_basic(extraction_data: Dict[str, Any]) -> tuple:
    """Basic processing of a single extraction without complex NLP"""
    concepts = []
    relationships = []
    
    repo_name = extraction_data['repository']
    
    for extraction in extraction_data['extractions']:
        if 'error' in extraction:
            continue
            
        file_path = extraction['file_path']
        content_type = extraction['content_type']
        content = extraction['content']
        title = extraction.get('title', '')
        summary = extraction.get('summary', '')
        key_terms = extraction.get('key_terms', [])
        
        # Extract concepts from the extraction
        file_concepts = extract_concepts_basic(
            repo_name, file_path, content_type, title, summary, key_terms
        )
        concepts.extend(file_concepts)
        
        # Extract relationships from the extraction
        file_relationships = extract_relationships_basic(
            repo_name, file_path, key_terms
        )
        relationships.extend(file_relationships)
    
    return concepts, relationships


def extract_concepts_basic(repo_name: str, file_path: str, content_type: str, 
                         title: str, summary: str, key_terms: List[str]) -> List[Dict[str, Any]]:
    """Basic concept extraction without complex NLP"""
    concepts = []
    
    # Add title as a concept
    if title and title != "No Title Found":
        concept = {
            'name': title,
            'type': 'title',
            'source_repo': repo_name,
            'source_file': file_path,
            'context': summary[:100] + "..." if len(summary) > 100 else summary,
            'description': summary,
            'tags': [content_type, 'title'],
            'timestamp': datetime.now().isoformat()
        }
        concepts.append(concept)
    
    # Add key terms as concepts
    for term in key_terms:
        concept = {
            'name': term,
            'type': 'term',
            'source_repo': repo_name,
            'source_file': file_path,
            'context': title,
            'description': summary,
            'tags': [content_type, 'term'],
            'timestamp': datetime.now().isoformat()
        }
        concepts.append(concept)
    
    # Add file path elements as potential concepts
    path_parts = Path(file_path).parts
    for part in path_parts:
        if len(part) > 2 and not part.endswith(('.py', '.ts', '.js', '.go', '.rs', '.ex', '.md', '.json', '.yaml', '.yml')):
            concept = {
                'name': part,
                'type': 'path_component',
                'source_repo': repo_name,
                'source_file': file_path,
                'context': title,
                'description': f"Part of file path: {file_path}",
                'tags': ['path', 'structure'],
                'timestamp': datetime.now().isoformat()
            }
            concepts.append(concept)
    
    return concepts


def extract_relationships_basic(repo_name: str, file_path: str, key_terms: List[str]) -> List[Dict[str, Any]]:
    """Basic relationship extraction without complex NLP"""
    relationships = []
    
    # Create relationships between key terms in the same file
    for i, term1 in enumerate(key_terms):
        for term2 in key_terms[i+1:]:
            if term1 != term2:
                relationship = {
                    'source': term1,
                    'target': term2,
                    'type': 'co_occurrence',
                    'strength': 0.5,
                    'source_repo': repo_name,
                    'source_file': file_path,
                    'context': f"Terms '{term1}' and '{term2}' appear in the same file: {file_path}",
                    'timestamp': datetime.now().isoformat()
                }
                relationships.append(relationship)
    
    # Create relationships between repository and terms
    for term in key_terms:
        relationship = {
            'source': repo_name,
            'target': term,
            'type': 'contains',
            'strength': 0.8,
            'source_repo': repo_name,
            'source_file': file_path,
            'context': f"Repository {repo_name} contains term '{term}'",
            'timestamp': datetime.now().isoformat()
        }
        relationships.append(relationship)
    
    return relationships


def save_processed_knowledge(concepts: List[Dict], relationships: List[Dict], 
                           output_dir: Path):
    """Save processed knowledge to the appropriate directories"""
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save concepts
    concepts_path = output_dir / "all_concepts.json"
    with open(concepts_path, 'w', encoding='utf-8') as f:
        json.dump(concepts, f, indent=2)
    
    # Save relationships
    relationships_path = output_dir / "all_relationships.json"
    with open(relationships_path, 'w', encoding='utf-8') as f:
        json.dump(relationships, f, indent=2)
    
    # Create summary files
    create_summaries(concepts, relationships, output_dir)


def create_summaries(concepts: List[Dict], relationships: List[Dict], output_dir: Path):
    """Create summary files for quick access to knowledge"""
    # Create concept summary
    concept_types = Counter([c['type'] for c in concepts])
    concept_sources = Counter([c['source_repo'] for c in concepts])
    
    concept_summary = {
        'total_concepts': len(concepts),
        'concept_types': dict(concept_types),
        'source_repositories': dict(concept_sources),
        'timestamp': datetime.now().isoformat()
    }
    
    summary_path = output_dir / "concepts_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(concept_summary, f, indent=2)
    
    # Create relationship summary
    relationship_types = Counter([r['type'] for r in relationships])
    relationship_sources = Counter([r['source_repo'] for r in relationships])
    
    relationship_summary = {
        'total_relationships': len(relationships),
        'relationship_types': dict(relationship_types),
        'source_repositories': dict(relationship_sources),
        'timestamp': datetime.now().isoformat()
    }
    
    summary_path = output_dir / "relationships_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(relationship_summary, f, indent=2)


def extract_wisdom_basic(concepts: List[Dict], relationships: List[Dict], output_dir: Path):
    """Basic wisdom extraction focusing on patterns and principles"""
    # Identify potential principles (terms that appear frequently across repos)
    term_repo_counts = defaultdict(set)
    for concept in concepts:
        term_repo_counts[concept['name']].add(concept['source_repo'])
    
    # Terms that appear in multiple repositories might be core principles
    potential_principles = [
        term for term, repos in term_repo_counts.items() 
        if len(repos) > 1 and len(term) > 3
    ]
    
    principles = []
    for term in potential_principles:
        repos = list(term_repo_counts[term])
        principle = {
            'name': term,
            'description': f"Concept '{term}' appears in multiple repositories: {', '.join(repos)}",
            'source_repositories': repos,
            'timestamp': datetime.now().isoformat()
        }
        principles.append(principle)
    
    # Save principles
    wisdom_dir = output_dir.parent / "wisdom" / "principles"
    wisdom_dir.mkdir(parents=True, exist_ok=True)
    
    principles_path = wisdom_dir / "all_principles.json"
    with open(principles_path, 'w', encoding='utf-8') as f:
        json.dump(principles, f, indent=2)
    
    # Create patterns from common relationship types
    relationship_patterns = Counter([r['type'] for r in relationships])
    patterns = []
    for pattern_type, count in relationship_patterns.most_common(10):
        pattern = {
            'name': f"{pattern_type}_pattern",
            'description': f"Relationship pattern '{pattern_type}' appears {count} times",
            'frequency': count,
            'timestamp': datetime.now().isoformat()
        }
        patterns.append(pattern)
    
    # Save patterns
    patterns_dir = output_dir.parent / "wisdom" / "patterns"
    patterns_dir.mkdir(parents=True, exist_ok=True)
    
    patterns_path = patterns_dir / "all_patterns.json"
    with open(patterns_path, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2)


def main():
    """Main function for basic processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Basic UTCP Knowledge Processor")
    parser.add_argument("--input-dir", default=".utcp-kb/raw-extractions", 
                       help="Input directory containing raw extractions")
    parser.add_argument("--output-dir", default=".utcp-kb/processed-knowledge", 
                       help="Output directory for processed knowledge")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    print("Loading raw extractions...")
    extractions = load_raw_extractions(input_path)
    
    print(f"Processing {len(extractions)} extractions...")
    
    all_concepts = []
    all_relationships = []
    
    for extraction_data in extractions:
        concepts, relationships = process_extraction_basic(extraction_data)
        all_concepts.extend(concepts)
        all_relationships.extend(relationships)
    
    print(f"Processed {len(all_concepts)} concepts and {len(all_relationships)} relationships")
    
    # Save processed knowledge
    save_processed_knowledge(all_concepts, all_relationships, output_path)
    
    # Extract wisdom
    extract_wisdom_basic(all_concepts, all_relationships, output_path)
    
    print("Basic processing completed!")


if __name__ == "__main__":
    main()