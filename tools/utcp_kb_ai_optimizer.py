#!/usr/bin/env python3
"""
UTCP Knowledge Base AI Optimization System
Optimizes knowledge for AI consumption and retrieval
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss


class UTCPAIOptimizer:
    """Main class for optimizing knowledge for AI consumption"""
    
    def __init__(self, config_path: str = ".utcp-kb/config/extraction_config.json"):
        self.config_path = config_path
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        self.load_embedding_model()
        
    def setup_logging(self):
        """Set up logging for the AI optimization process"""
        log_dir = Path(".utcp-kb/logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"ai_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_embedding_model(self):
        """Load the embedding model for vector generation"""
        try:
            model_name = self.config['ai_optimization']['embedding_model']
            self.embedding_model = SentenceTransformer(model_name)
            self.logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            self.logger.warning(f"Could not load embedding model {self.config['ai_optimization']['embedding_model']}: {e}")
            self.logger.info("Using basic TF-IDF vectorization instead")
            self.embedding_model = None
            self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def generate_embeddings(self):
        """Generate embeddings for all knowledge components"""
        self.logger.info("Starting AI optimization: generating embeddings")
        
        # Process concepts
        self.process_concepts_for_ai()
        
        # Process relationships
        self.process_relationships_for_ai()
        
        # Process repositories information
        self.process_repositories_for_ai()
        
        # Process wisdom components
        self.process_wisdom_for_ai()
        
        # Create knowledge graph embeddings
        self.create_knowledge_graph_embeddings()
        
        # Generate summaries optimized for AI
        self.generate_ai_optimized_summaries()
        
        self.logger.info("Completed AI optimization")
    
    def process_concepts_for_ai(self):
        """Process concepts for AI optimization"""
        concepts_path = Path(".utcp-kb/processed-knowledge/concepts/all_concepts.json")
        
        if not concepts_path.exists():
            self.logger.warning("No concepts file found, skipping concept processing")
            return
        
        with open(concepts_path, 'r', encoding='utf-8') as f:
            concepts = json.load(f)
        
        # Prepare text data for embedding
        texts = []
        metadata = []
        
        for concept in concepts:
            text = f"{concept['name']} {concept['description']} {concept['context']}"
            texts.append(text)
            metadata.append({
                'id': concept.get('id', len(metadata)),
                'name': concept['name'],
                'type': concept['type'],
                'source_repo': concept['source_repo'],
                'source_file': concept['source_file'],
                'timestamp': concept['timestamp']
            })
        
        # Generate embeddings
        if self.embedding_model:
            embeddings = self.embedding_model.encode(texts)
        else:
            # Use TF-IDF as fallback
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            embeddings = tfidf_matrix.toarray()
        
        # Save embeddings and metadata
        embeddings_dir = Path(".utcp-kb/ai-optimized/embeddings")
        embeddings_dir.mkdir(exist_ok=True)
        
        # Save embeddings
        embeddings_path = embeddings_dir / "concepts_embeddings.npy"
        np.save(embeddings_path, embeddings)
        
        # Save metadata
        metadata_path = embeddings_dir / "concepts_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Create FAISS index for fast similarity search
        self.create_faiss_index(embeddings, embeddings_dir / "concepts.index")
        
        self.logger.info(f"Processed {len(concepts)} concepts for AI optimization")
    
    def process_relationships_for_ai(self):
        """Process relationships for AI optimization"""
        relationships_path = Path(".utcp-kb/processed-knowledge/relationships/all_relationships.json")
        
        if not relationships_path.exists():
            self.logger.warning("No relationships file found, skipping relationship processing")
            return
        
        with open(relationships_path, 'r', encoding='utf-8') as f:
            relationships = json.load(f)
        
        # Prepare text data for embedding
        texts = []
        metadata = []
        
        for rel in relationships:
            text = f"{rel['source']} {rel['type']} {rel['target']} {rel['context']}"
            texts.append(text)
            metadata.append({
                'id': rel.get('id', len(metadata)),
                'source': rel['source'],
                'target': rel['target'],
                'type': rel['type'],
                'strength': rel['strength'],
                'source_repo': rel['source_repo'],
                'source_file': rel['source_file'],
                'timestamp': rel['timestamp']
            })
        
        # Generate embeddings
        if self.embedding_model:
            embeddings = self.embedding_model.encode(texts)
        else:
            # Use TF-IDF as fallback
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            embeddings = tfidf_matrix.toarray()
        
        # Save embeddings and metadata
        embeddings_dir = Path(".utcp-kb/ai-optimized/embeddings")
        
        # Save embeddings
        embeddings_path = embeddings_dir / "relationships_embeddings.npy"
        np.save(embeddings_path, embeddings)
        
        # Save metadata
        metadata_path = embeddings_dir / "relationships_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Create FAISS index
        self.create_faiss_index(embeddings, embeddings_dir / "relationships.index")
        
        self.logger.info(f"Processed {len(relationships)} relationships for AI optimization")
    
    def process_repositories_for_ai(self):
        """Process repositories information for AI optimization"""
        repos_path = Path(".utcp-kb/processed-knowledge/repositories/all_repositories.json")
        
        if not repos_path.exists():
            self.logger.warning("No repositories file found, skipping repository processing")
            return
        
        with open(repos_path, 'r', encoding='utf-8') as f:
            repositories = json.load(f)
        
        # Prepare text data for embedding
        texts = []
        metadata = []
        
        for repo in repositories:
            text = f"{repo['name']} {repo['name']} implementation details"
            texts.append(text)
            metadata.append({
                'id': repo.get('id', len(metadata)),
                'name': repo['name'],
                'commit_hash': repo['commit_hash'],
                'file_count': repo['file_count'],
                'extraction_date': repo['extraction_date'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Generate embeddings
        if self.embedding_model:
            embeddings = self.embedding_model.encode(texts)
        else:
            # Use TF-IDF as fallback
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            embeddings = tfidf_matrix.toarray()
        
        # Save embeddings and metadata
        embeddings_dir = Path(".utcp-kb/ai-optimized/embeddings")
        
        # Save embeddings
        embeddings_path = embeddings_dir / "repositories_embeddings.npy"
        np.save(embeddings_path, embeddings)
        
        # Save metadata
        metadata_path = embeddings_dir / "repositories_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Processed {len(repositories)} repositories for AI optimization")
    
    def process_wisdom_for_ai(self):
        """Process wisdom components for AI optimization"""
        wisdom_categories = ['principles', 'patterns', 'best_practices', 'insights']
        
        for category in wisdom_categories:
            wisdom_path = Path(f".utcp-kb/wisdom/{category}/all_{category}.json")
            
            if not wisdom_path.exists():
                self.logger.warning(f"No {category} file found, skipping")
                continue
            
            with open(wisdom_path, 'r', encoding='utf-8') as f:
                wisdom_items = json.load(f)
            
            # Prepare text data for embedding
            texts = []
            metadata = []
            
            for item in wisdom_items:
                text = f"{item['name']} {item['description']} {item['context'] if 'context' in item else ''}"
                texts.append(text)
                metadata.append({
                    'id': item.get('id', len(metadata)),
                    'name': item['name'],
                    'description': item['description'],
                    'source_repo': item.get('source_repo', 'unknown'),
                    'source_file': item.get('source_file', 'unknown'),
                    'timestamp': item.get('timestamp', datetime.now().isoformat())
                })
            
            # Generate embeddings
            if self.embedding_model:
                embeddings = self.embedding_model.encode(texts)
            else:
                # Use TF-IDF as fallback
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
                embeddings = tfidf_matrix.toarray()
            
            # Save embeddings and metadata
            embeddings_dir = Path(".utcp-kb/ai-optimized/embeddings")
            
            # Save embeddings
            embeddings_path = embeddings_dir / f"{category}_embeddings.npy"
            np.save(embeddings_path, embeddings)
            
            # Save metadata
            metadata_path = embeddings_dir / f"{category}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Create FAISS index
            self.create_faiss_index(embeddings, embeddings_dir / f"{category}.index")
            
            self.logger.info(f"Processed {len(wisdom_items)} {category} for AI optimization")
    
    def create_faiss_index(self, embeddings: np.ndarray, index_path: Path):
        """Create a FAISS index for fast similarity search"""
        try:
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Create index (use IndexFlatIP for inner product which is cosine similarity after normalization)
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            
            # Add embeddings to index
            index.add(embeddings.astype('float32'))
            
            # Save index
            faiss.write_index(index, str(index_path))
            
            self.logger.info(f"Created FAISS index with {embeddings.shape[0]} vectors at {index_path}")
        except Exception as e:
            self.logger.warning(f"Could not create FAISS index: {e}")
    
    def create_knowledge_graph_embeddings(self):
        """Create embeddings that represent the knowledge graph structure"""
        self.logger.info("Creating knowledge graph embeddings")
        
        # Load all processed data
        concepts_path = Path(".utcp-kb/processed-knowledge/concepts/all_concepts.json")
        relationships_path = Path(".utcp-kb/processed-knowledge/relationships/all_relationships.json")
        
        if not concepts_path.exists() or not relationships_path.exists():
            self.logger.warning("Missing concepts or relationships, skipping knowledge graph creation")
            return
        
        with open(concepts_path, 'r', encoding='utf-8') as f:
            concepts = json.load(f)
        
        with open(relationships_path, 'r', encoding='utf-8') as f:
            relationships = json.load(f)
        
        # Create a graph representation
        graph_texts = []
        graph_metadata = []
        
        # Add concept-to-concept relationships through shared contexts
        concept_map = {c['name']: c for c in concepts}
        
        for rel in relationships:
            source_concept = concept_map.get(rel['source'])
            target_concept = concept_map.get(rel['target'])
            
            if source_concept and target_concept:
                text = f"The {source_concept['type']} '{source_concept['name']}' has a '{rel['type']}' relationship with the {target_concept['type']} '{target_concept['name']}' in the context of {rel['context']}"
                
                graph_texts.append(text)
                graph_metadata.append({
                    'relationship_type': rel['type'],
                    'source': rel['source'],
                    'target': rel['target'],
                    'strength': rel['strength'],
                    'source_repo': rel['source_repo']
                })
        
        # Generate embeddings for graph relationships
        if graph_texts and self.embedding_model:
            embeddings = self.embedding_model.encode(graph_texts)
        elif graph_texts:
            # Use TF-IDF as fallback
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(graph_texts)
            embeddings = tfidf_matrix.toarray()
        else:
            self.logger.info("No graph relationships to process")
            return
        
        # Save graph embeddings
        embeddings_dir = Path(".utcp-kb/ai-optimized/embeddings")
        graph_embeddings_path = embeddings_dir / "knowledge_graph_embeddings.npy"
        np.save(graph_embeddings_path, embeddings)
        
        # Save graph metadata
        graph_metadata_path = embeddings_dir / "knowledge_graph_metadata.json"
        with open(graph_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(graph_metadata, f, indent=2)
        
        # Create FAISS index for graph
        self.create_faiss_index(embeddings, embeddings_dir / "knowledge_graph.index")
        
        self.logger.info(f"Created knowledge graph with {len(graph_texts)} relationships")
    
    def generate_ai_optimized_summaries(self):
        """Generate summaries optimized for AI consumption"""
        self.logger.info("Generating AI-optimized summaries")
        
        summaries_dir = Path(".utcp-kb/ai-optimized/summaries")
        summaries_dir.mkdir(exist_ok=True)
        
        # Generate a comprehensive summary of the entire knowledge base
        summary_data = {
            'kb_overview': self.generate_overview_summary(),
            'concepts_summary': self.generate_concepts_summary(),
            'relationships_summary': self.generate_relationships_summary(),
            'repositories_summary': self.generate_repositories_summary(),
            'wisdom_summary': self.generate_wisdom_summary(),
            'timestamp': datetime.now().isoformat()
        }
        
        summary_path = summaries_dir / "comprehensive_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2)
        
        # Generate topic-specific summaries
        self.generate_topic_summaries()
        
        self.logger.info("Completed AI-optimized summaries")
    
    def generate_overview_summary(self) -> str:
        """Generate an overview summary of the knowledge base"""
        # Load summary files to get counts
        concept_summary_path = Path(".utcp-kb/processed-knowledge/concepts/summary.json")
        relationship_summary_path = Path(".utcp-kb/processed-knowledge/relationships/summary.json")
        repo_summary_path = Path(".utcp-kb/processed-knowledge/repositories/summary.json")
        wisdom_summary_path = Path(".utcp-kb/wisdom/summary.json")
        
        overview_parts = ["UTCP Knowledge Base Overview:"]
        
        if concept_summary_path.exists():
            with open(concept_summary_path, 'r', encoding='utf-8') as f:
                concept_summary = json.load(f)
            overview_parts.append(f"- {concept_summary['total_concepts']} concepts across {len(concept_summary['concept_types'])} types")
        
        if relationship_summary_path.exists():
            with open(relationship_summary_path, 'r', encoding='utf-8') as f:
                relationship_summary = json.load(f)
            overview_parts.append(f"- {relationship_summary['total_relationships']} relationships across {len(relationship_summary['relationship_types'])} types")
        
        if repo_summary_path.exists():
            with open(repo_summary_path, 'r', encoding='utf-8') as f:
                repo_summary = json.load(f)
            overview_parts.append(f"- {repo_summary['total_repositories']} repositories analyzed")
        
        if wisdom_summary_path.exists():
            with open(wisdom_summary_path, 'r', encoding='utf-8') as f:
                wisdom_summary = json.load(f)
            overview_parts.append(f"- {wisdom_summary['total_principles']} principles, {wisdom_summary['total_patterns']} patterns, {wisdom_summary['total_best_practices']} best practices, {wisdom_summary['total_insights']} insights")
        
        return " ".join(overview_parts)
    
    def generate_concepts_summary(self) -> Dict[str, Any]:
        """Generate a summary of concepts optimized for AI"""
        concepts_path = Path(".utcp-kb/processed-knowledge/concepts/all_concepts.json")
        
        if not concepts_path.exists():
            return {}
        
        with open(concepts_path, 'r', encoding='utf-8') as f:
            concepts = json.load(f)
        
        # Group concepts by type and source repository
        concepts_by_type = {}
        concepts_by_repo = {}
        
        for concept in concepts:
            # Group by type
            concept_type = concept['type']
            if concept_type not in concepts_by_type:
                concepts_by_type[concept_type] = []
            concepts_by_type[concept_type].append({
                'name': concept['name'],
                'description': concept['description']
            })
            
            # Group by repository
            repo = concept['source_repo']
            if repo not in concepts_by_repo:
                concepts_by_repo[repo] = []
            concepts_by_repo[repo].append({
                'name': concept['name'],
                'type': concept['type']
            })
        
        return {
            'total_concepts': len(concepts),
            'by_type': concepts_by_type,
            'by_repository': concepts_by_repo
        }
    
    def generate_relationships_summary(self) -> Dict[str, Any]:
        """Generate a summary of relationships optimized for AI"""
        relationships_path = Path(".utcp-kb/processed-knowledge/relationships/all_relationships.json")
        
        if not relationships_path.exists():
            return {}
        
        with open(relationships_path, 'r', encoding='utf-8') as f:
            relationships = json.load(f)
        
        # Group relationships by type
        relationships_by_type = {}
        relationships_by_repo = {}
        
        for rel in relationships:
            # Group by type
            rel_type = rel['type']
            if rel_type not in relationships_by_type:
                relationships_by_type[rel_type] = []
            relationships_by_type[rel_type].append({
                'source': rel['source'],
                'target': rel['target'],
                'strength': rel['strength']
            })
            
            # Group by repository
            repo = rel['source_repo']
            if repo not in relationships_by_repo:
                relationships_by_repo[repo] = []
            relationships_by_repo[repo].append({
                'source': rel['source'],
                'target': rel['target'],
                'type': rel['type']
            })
        
        return {
            'total_relationships': len(relationships),
            'by_type': relationships_by_type,
            'by_repository': relationships_by_repo
        }
    
    def generate_repositories_summary(self) -> Dict[str, Any]:
        """Generate a summary of repositories optimized for AI"""
        repos_path = Path(".utcp-kb/processed-knowledge/repositories/all_repositories.json")
        
        if not repos_path.exists():
            return {}
        
        with open(repos_path, 'r', encoding='utf-8') as f:
            repositories = json.load(f)
        
        return {
            'total_repositories': len(repositories),
            'repository_details': [
                {
                    'name': repo['name'],
                    'file_count': repo['file_count'],
                    'last_extraction': repo['extraction_date']
                }
                for repo in repositories
            ]
        }
    
    def generate_wisdom_summary(self) -> Dict[str, Any]:
        """Generate a summary of wisdom components optimized for AI"""
        wisdom_categories = ['principles', 'patterns', 'best_practices', 'insights']
        wisdom_summary = {}
        
        for category in wisdom_categories:
            wisdom_path = Path(f".utcp-kb/wisdom/{category}/all_{category}.json")
            
            if wisdom_path.exists():
                with open(wisdom_path, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                
                wisdom_summary[category] = {
                    'count': len(items),
                    'items': [
                        {
                            'name': item['name'],
                            'description': item['description']
                        }
                        for item in items
                    ]
                }
            else:
                wisdom_summary[category] = {'count': 0, 'items': []}
        
        return wisdom_summary
    
    def generate_topic_summaries(self):
        """Generate topic-specific summaries"""
        # This would identify key topics and create focused summaries
        # For now, we'll create a simple implementation
        
        # Load all concepts to identify key topics
        concepts_path = Path(".utcp-kb/processed-knowledge/concepts/all_concepts.json")
        
        if not concepts_path.exists():
            return
        
        with open(concepts_path, 'r', encoding='utf-8') as f:
            concepts = json.load(f)
        
        # Identify key topics based on concept names and types
        topics = {}
        for concept in concepts:
            # Use the first word or common terms as topics
            name_parts = concept['name'].lower().split()
            if name_parts:
                topic = name_parts[0]
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(concept['name'])
        
        # Create topic summaries
        summaries_dir = Path(".utcp-kb/ai-optimized/summaries")
        
        for topic, concept_list in topics.items():
            topic_summary = {
                'topic': topic,
                'related_concepts': concept_list,
                'count': len(concept_list),
                'timestamp': datetime.now().isoformat()
            }
            
            topic_path = summaries_dir / f"topic_{topic}_summary.json"
            with open(topic_path, 'w', encoding='utf-8') as f:
                json.dump(topic_summary, f, indent=2)


def main():
    """Main function to run the AI optimization system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UTCP Knowledge Base AI Optimization System")
    parser.add_argument("--config", default=".utcp-kb/config/extraction_config.json", help="Path to configuration file")
    
    args = parser.parse_args()
    
    optimizer = UTCPAIOptimizer(config_path=args.config)
    optimizer.generate_embeddings()


if __name__ == "__main__":
    main()