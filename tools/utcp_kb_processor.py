#!/usr/bin/env python3
"""
UTCP Knowledge Base Processing System
Processes raw extractions into structured knowledge
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Set
import logging
from datetime import datetime
import spacy
from collections import defaultdict, Counter


class UTCPKnowledgeProcessor:
    """Main class for processing extracted knowledge into structured formats"""
    
    def __init__(self, config_path: str = ".utcp-kb/config/extraction_config.json"):
        self.config_path = config_path
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        self.load_nlp_model()
        
    def setup_logging(self):
        """Set up logging for the processing process"""
        log_dir = Path(".utcp-kb/logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_nlp_model(self):
        """Load the NLP model for text processing"""
        try:
            # Try to load the model, if it doesn't exist we'll handle it gracefully
            self.nlp = spacy.load(self.config['processing']['nlp_model'])
        except OSError:
            self.logger.warning(f"NLP model {self.config['processing']['nlp_model']} not found, using basic processing")
            # For now, we'll use a simpler approach without spaCy
            self.nlp = None
    
    def process_raw_extractions(self):
        """Process all raw extractions into structured knowledge"""
        self.logger.info("Starting processing of raw extractions")
        
        # Get all raw extraction files
        raw_extraction_dir = Path(".utcp-kb/raw-extractions")
        repo_dirs = [d for d in raw_extraction_dir.iterdir() if d.is_dir()]
        
        all_concepts = []
        all_relationships = []
        all_repositories = []
        all_evolution = []
        
        for repo_dir in repo_dirs:
            self.logger.info(f"Processing repository: {repo_dir.name}")
            
            # Process each extraction file in the repository
            extraction_files = list(repo_dir.glob("extraction_*.json"))
            
            for extraction_file in extraction_files:
                with open(extraction_file, 'r', encoding='utf-8') as f:
                    extraction_data = json.load(f)
                
                # Process the extraction data
                repo_concepts, repo_relationships = self.process_extraction(extraction_data)
                
                all_concepts.extend(repo_concepts)
                all_relationships.extend(repo_relationships)
                
                # Add repository-specific information
                all_repositories.append({
                    'name': extraction_data['repository'],
                    'commit_hash': extraction_data['commit_hash'],
                    'commit_date': extraction_data['commit_date'],
                    'file_count': extraction_data['file_count'],
                    'extraction_date': extraction_data['timestamp']
                })
        
        # Organize and save processed knowledge
        self.save_processed_knowledge(all_concepts, all_relationships, all_repositories, all_evolution)
        
        # Extract wisdom from the processed knowledge
        self.extract_wisdom(all_concepts, all_relationships)
        
        self.logger.info("Completed processing of raw extractions")
    
    def process_extraction(self, extraction_data: Dict[str, Any]) -> tuple:
        """Process a single extraction and return concepts and relationships"""
        concepts = []
        relationships = []
        
        repo_name = extraction_data['repository']
        
        for extraction in extraction_data['extractions']:
            if 'error' in extraction:
                continue
                
            file_path = extraction['file_path']
            content_type = extraction['content_type']
            content = extraction['content']
            extracted_info = extraction['extracted_info']
            
            # Extract concepts from the extraction
            file_concepts = self.extract_concepts_from_extraction(
                repo_name, file_path, content_type, content, extracted_info
            )
            concepts.extend(file_concepts)
            
            # Extract relationships from the extraction
            file_relationships = self.extract_relationships_from_extraction(
                repo_name, file_path, content_type, content, extracted_info
            )
            relationships.extend(file_relationships)
        
        return concepts, relationships
    
    def extract_concepts_from_extraction(self, repo_name: str, file_path: str, 
                                       content_type: str, content: str, 
                                       extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract concepts from a single extraction"""
        concepts = []
        
        # Extract concepts based on content type
        if content_type == 'code':
            # Extract concepts from code elements
            for func in extracted_info.get('functions', []):
                concept = {
                    'name': func,
                    'type': 'function',
                    'source_repo': repo_name,
                    'source_file': file_path,
                    'context': extracted_info.get('title', ''),
                    'description': extracted_info.get('summary', ''),
                    'tags': ['code', 'function'],
                    'timestamp': datetime.now().isoformat()
                }
                concepts.append(concept)
            
            for cls in extracted_info.get('classes', []):
                concept = {
                    'name': cls,
                    'type': 'class',
                    'source_repo': repo_name,
                    'source_file': file_path,
                    'context': extracted_info.get('title', ''),
                    'description': extracted_info.get('summary', ''),
                    'tags': ['code', 'class'],
                    'timestamp': datetime.now().isoformat()
                }
                concepts.append(concept)
        
        elif content_type in ['documentation', 'specification']:
            # Extract concepts from documentation
            for section in extracted_info.get('sections', []):
                concept = {
                    'name': section,
                    'type': 'section',
                    'source_repo': repo_name,
                    'source_file': file_path,
                    'context': extracted_info.get('title', ''),
                    'description': extracted_info.get('summary', ''),
                    'tags': ['documentation', 'section'],
                    'timestamp': datetime.now().isoformat()
                }
                concepts.append(concept)
        
        # Add key terms as concepts
        for term in extracted_info.get('key_terms', []):
            concept = {
                'name': term,
                'type': 'term',
                'source_repo': repo_name,
                'source_file': file_path,
                'context': extracted_info.get('title', ''),
                'description': extracted_info.get('summary', ''),
                'tags': ['term'],
                'timestamp': datetime.now().isoformat()
            }
            concepts.append(concept)
        
        # Extract concepts using NLP if available
        if self.nlp:
            doc = self.nlp(content[:10000])  # Limit to first 10k chars to avoid memory issues
            
            # Extract named entities as concepts
            for ent in doc.ents:
                if len(ent.text.strip()) > 2:  # Filter out very short entities
                    concept = {
                        'name': ent.text,
                        'type': ent.label_,
                        'source_repo': repo_name,
                        'source_file': file_path,
                        'context': extracted_info.get('title', ''),
                        'description': ent.text,
                        'tags': ['nlp', 'entity'],
                        'timestamp': datetime.now().isoformat()
                    }
                    concepts.append(concept)
        
        return concepts
    
    def extract_relationships_from_extraction(self, repo_name: str, file_path: str, 
                                            content_type: str, content: str, 
                                            extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relationships from a single extraction"""
        relationships = []
        
        # Create relationships between functions/classes in code
        if content_type == 'code':
            functions = extracted_info.get('functions', [])
            classes = extracted_info.get('classes', [])
            
            # Relationships between functions in the same file
            for i, func1 in enumerate(functions):
                for func2 in functions[i+1:]:
                    if func1 != func2:
                        relationship = {
                            'source': func1,
                            'target': func2,
                            'type': 'same_file',
                            'strength': 1.0,
                            'source_repo': repo_name,
                            'source_file': file_path,
                            'context': f"Both functions appear in {file_path}",
                            'timestamp': datetime.now().isoformat()
                        }
                        relationships.append(relationship)
            
            # Relationships between classes and functions in the same file
            for cls in classes:
                for func in functions:
                    relationship = {
                        'source': cls,
                        'target': func,
                        'type': 'contains',
                        'strength': 0.8,
                        'source_repo': repo_name,
                        'source_file': file_path,
                        'context': f"Class {cls} may contain or use function {func}",
                        'timestamp': datetime.now().isoformat()
                    }
                    relationships.append(relationship)
        
        # Create relationships based on shared key terms
        key_terms = extracted_info.get('key_terms', [])
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
                        'context': f"Terms '{term1}' and '{term2}' appear in the same document",
                        'timestamp': datetime.now().isoformat()
                    }
                    relationships.append(relationship)
        
        return relationships
    
    def save_processed_knowledge(self, concepts: List[Dict], relationships: List[Dict], 
                               repositories: List[Dict], evolution: List[Dict]):
        """Save processed knowledge to the appropriate directories"""
        # Save concepts
        concepts_path = Path(".utcp-kb/processed-knowledge/concepts/all_concepts.json")
        with open(concepts_path, 'w', encoding='utf-8') as f:
            json.dump(concepts, f, indent=2)
        
        # Save relationships
        relationships_path = Path(".utcp-kb/processed-knowledge/relationships/all_relationships.json")
        with open(relationships_path, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, indent=2)
        
        # Save repositories info
        repos_path = Path(".utcp-kb/processed-knowledge/repositories/all_repositories.json")
        with open(repos_path, 'w', encoding='utf-8') as f:
            json.dump(repositories, f, indent=2)
        
        # Save evolution info (currently empty, but structure is there)
        evolution_path = Path(".utcp-kb/processed-knowledge/evolution/all_evolution.json")
        with open(evolution_path, 'w', encoding='utf-8') as f:
            json.dump(evolution, f, indent=2)
        
        # Create summary files
        self.create_summaries(concepts, relationships, repositories)
    
    def create_summaries(self, concepts: List[Dict], relationships: List[Dict], repositories: List[Dict]):
        """Create summary files for quick access to knowledge"""
        # Create concept summary
        concept_types = Counter([c['type'] for c in concepts])
        concept_summary = {
            'total_concepts': len(concepts),
            'concept_types': dict(concept_types),
            'repositories': list(set([c['source_repo'] for c in concepts])),
            'timestamp': datetime.now().isoformat()
        }
        
        summary_path = Path(".utcp-kb/processed-knowledge/concepts/summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(concept_summary, f, indent=2)
        
        # Create relationship summary
        relationship_types = Counter([r['type'] for r in relationships])
        relationship_summary = {
            'total_relationships': len(relationships),
            'relationship_types': dict(relationship_types),
            'timestamp': datetime.now().isoformat()
        }
        
        summary_path = Path(".utcp-kb/processed-knowledge/relationships/summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(relationship_summary, f, indent=2)
        
        # Create repository summary
        repo_summary = {
            'total_repositories': len(repositories),
            'repositories': [r['name'] for r in repositories],
            'timestamp': datetime.now().isoformat()
        }
        
        summary_path = Path(".utcp-kb/processed-knowledge/repositories/summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(repo_summary, f, indent=2)
    
    def extract_wisdom(self, concepts: List[Dict], relationships: List[Dict]):
        """Extract wisdom, principles, patterns, and best practices from the knowledge"""
        self.logger.info("Extracting wisdom from processed knowledge")
        
        # Identify common patterns and principles
        principles = self.extract_principles(concepts, relationships)
        patterns = self.extract_patterns(concepts, relationships)
        best_practices = self.extract_best_practices(concepts, relationships)
        insights = self.extract_insights(concepts, relationships)
        
        # Save wisdom components
        self.save_wisdom(principles, patterns, best_practices, insights)
    
    def extract_principles(self, concepts: List[Dict], relationships: List[Dict]) -> List[Dict]:
        """Extract core principles from the knowledge"""
        principles = []
        
        # Look for concepts with names that suggest principles
        principle_indicators = [
            'principle', 'pattern', 'design', 'architecture', 'protocol', 
            'standard', 'specification', 'rule', 'guideline'
        ]
        
        for concept in concepts:
            concept_name = concept['name'].lower()
            if any(indicator in concept_name for indicator in principle_indicators):
                principle = {
                    'name': concept['name'],
                    'description': concept['description'],
                    'source_repo': concept['source_repo'],
                    'source_file': concept['source_file'],
                    'context': concept['context'],
                    'timestamp': datetime.now().isoformat()
                }
                principles.append(principle)
        
        # Add known UTCP principles based on repository analysis
        utcp_principles = [
            {
                'name': 'Universal Tool Calling',
                'description': 'A protocol that lets AI agents call any native endpoint, over any channel - directly and without wrappers',
                'source_repo': 'utcp-specification',
                'source_file': 'specification',
                'context': 'Core UTCP principle',
                'timestamp': datetime.now().isoformat()
            },
            {
                'name': 'Direct Tool Access',
                'description': 'AI agents can call tools directly without extra middleware',
                'source_repo': 'utcp-specification',
                'source_file': 'specification',
                'context': 'Core UTCP principle',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        principles.extend(utcp_principles)
        
        return principles
    
    def extract_patterns(self, concepts: List[Dict], relationships: List[Dict]) -> List[Dict]:
        """Extract design and implementation patterns"""
        patterns = []
        
        # Look for concepts that might represent patterns
        pattern_indicators = [
            'pattern', 'architecture', 'design', 'model', 'approach', 
            'method', 'strategy', 'technique', 'implementation'
        ]
        
        for concept in concepts:
            concept_name = concept['name'].lower()
            if any(indicator in concept_name for indicator in pattern_indicators):
                pattern = {
                    'name': concept['name'],
                    'description': concept['description'],
                    'source_repo': concept['source_repo'],
                    'source_file': concept['source_file'],
                    'context': concept['context'],
                    'timestamp': datetime.now().isoformat()
                }
                patterns.append(pattern)
        
        return patterns
    
    def extract_best_practices(self, concepts: List[Dict], relationships: List[Dict]) -> List[Dict]:
        """Extract best practices from the knowledge"""
        best_practices = []
        
        # Look for concepts related to best practices
        practice_indicators = [
            'best practice', 'recommendation', 'guideline', 'should', 'must',
            'advice', 'tip', 'approach', 'method', 'procedure'
        ]
        
        # Look in comments and documentation for best practices
        for concept in concepts:
            if concept['type'] in ['comment', 'documentation', 'section']:
                content = concept['description'].lower()
                if any(indicator in content for indicator in practice_indicators):
                    practice = {
                        'name': f"Best Practice: {concept['name']}",
                        'description': concept['description'],
                        'source_repo': concept['source_repo'],
                        'source_file': concept['source_file'],
                        'context': concept['context'],
                        'timestamp': datetime.now().isoformat()
                    }
                    best_practices.append(practice)
        
        return best_practices
    
    def extract_insights(self, concepts: List[Dict], relationships: List[Dict]) -> List[Dict]:
        """Extract insights and observations from the knowledge"""
        insights = []
        
        # Look for relationships that might indicate insights
        for relationship in relationships:
            if relationship['strength'] > 0.7:  # Strong relationships might indicate insights
                insight = {
                    'name': f"Relationship: {relationship['source']} -> {relationship['target']}",
                    'description': relationship['context'],
                    'type': relationship['type'],
                    'strength': relationship['strength'],
                    'source_repo': relationship['source_repo'],
                    'source_file': relationship['source_file'],
                    'timestamp': datetime.now().isoformat()
                }
                insights.append(insight)
        
        return insights
    
    def save_wisdom(self, principles: List[Dict], patterns: List[Dict], 
                   best_practices: List[Dict], insights: List[Dict]):
        """Save wisdom components to the appropriate directories"""
        # Save principles
        principles_path = Path(".utcp-kb/wisdom/principles/all_principles.json")
        with open(principles_path, 'w', encoding='utf-8') as f:
            json.dump(principles, f, indent=2)
        
        # Save patterns
        patterns_path = Path(".utcp-kb/wisdom/patterns/all_patterns.json")
        with open(patterns_path, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2)
        
        # Save best practices
        practices_path = Path(".utcp-kb/wisdom/best_practices/all_best_practices.json")
        with open(practices_path, 'w', encoding='utf-8') as f:
            json.dump(best_practices, f, indent=2)
        
        # Save insights
        insights_path = Path(".utcp-kb/wisdom/insights/all_insights.json")
        with open(insights_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2)
        
        # Create wisdom summary
        wisdom_summary = {
            'total_principles': len(principles),
            'total_patterns': len(patterns),
            'total_best_practices': len(best_practices),
            'total_insights': len(insights),
            'timestamp': datetime.now().isoformat()
        }
        
        summary_path = Path(".utcp-kb/wisdom/summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(wisdom_summary, f, indent=2)


def main():
    """Main function to run the processing system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UTCP Knowledge Base Processing System")
    parser.add_argument("--config", default=".utcp-kb/config/extraction_config.json", help="Path to configuration file")
    
    args = parser.parse_args()
    
    processor = UTCPKnowledgeProcessor(config_path=args.config)
    processor.process_raw_extractions()


if __name__ == "__main__":
    main()