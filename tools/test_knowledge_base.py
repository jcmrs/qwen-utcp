#!/usr/bin/env python3
"""
Test script to verify that the UTCP knowledge base is properly structured
"""

import json
from pathlib import Path
import sys

def test_knowledge_base():
    """Test that the knowledge base files are properly structured"""
    print("Testing UTCP Knowledge Base Structure")
    print("=" * 40)

    # Test processed concepts
    concepts_path = Path(".utcp-kb/processed-knowledge/all_concepts.json")
    if concepts_path.exists():
        print(f"OK: Concepts file exists: {concepts_path}")
        with open(concepts_path, 'r', encoding='utf-8') as f:
            concepts = json.load(f)
        print(f"OK: Successfully loaded {len(concepts)} concepts")

        if concepts:
            sample = concepts[0]
            print(f"OK: Sample concept: '{sample['name']}' from '{sample['source_repo']}'")
    else:
        print(f"ERROR: Concepts file missing: {concepts_path}")
        return False

    # Test processed relationships
    relationships_path = Path(".utcp-kb/processed-knowledge/all_relationships.json")
    if relationships_path.exists():
        print(f"OK: Relationships file exists: {relationships_path}")
        with open(relationships_path, 'r', encoding='utf-8') as f:
            relationships = json.load(f)
        print(f"OK: Successfully loaded {len(relationships)} relationships")

        if relationships:
            sample = relationships[0]
            print(f"OK: Sample relationship: '{sample['source']} -> {sample['target']}'")
    else:
        print(f"ERROR: Relationships file missing: {relationships_path}")
        return False

    # Test raw extractions
    raw_dirs = list(Path(".utcp-kb/raw-extractions").iterdir())
    if raw_dirs:
        print(f"OK: Found {len(raw_dirs)} raw extraction directories")

        # Test one raw extraction
        for raw_dir in raw_dirs:
            if raw_dir.is_dir():
                extraction_files = list(raw_dir.glob("extraction_*.json"))
                if extraction_files:
                    with open(extraction_files[0], 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)
                    print(f"OK: Raw extraction from {raw_dir.name} has {len(raw_data['extractions'])} items")
                    break
    else:
        print("ERROR: No raw extraction directories found")
        return False

    # Test AI-optimized components
    embeddings_path = Path(".utcp-kb/ai-optimized/embeddings/concept_embeddings.json")
    if embeddings_path.exists():
        print(f"OK: Embeddings file exists: {embeddings_path}")
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            embeddings = json.load(f)
        print(f"OK: Successfully loaded embeddings for {len(embeddings['metadata'])} concepts")
    else:
        print(f"WARNING: Embeddings file missing: {embeddings_path}")

    # Test wisdom components
    principles_path = Path(".utcp-kb/wisdom/principles/all_principles.json")
    if principles_path.exists():
        print(f"OK: Principles file exists: {principles_path}")
        with open(principles_path, 'r', encoding='utf-8') as f:
            principles = json.load(f)
        print(f"OK: Successfully loaded {len(principles)} principles")
    else:
        print(f"WARNING: Principles file missing: {principles_path}")

    print("=" * 40)
    print("Knowledge base structure test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_knowledge_base()
    if success:
        print("\nAll tests passed! The UTCP knowledge base is properly structured.")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)