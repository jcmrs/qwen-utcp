#!/usr/bin/env python3
"""
UTCP Knowledge Base Main Orchestration System
Coordinates extraction, processing, and AI optimization of UTCP knowledge
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime
import subprocess


class UTCPKnowledgeSystem:
    """Main orchestration class for the UTCP knowledge system"""
    
    def __init__(self, config_path: str = ".utcp-kb/config/extraction_config.json"):
        self.config_path = config_path
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging for the system"""
        log_dir = Path(".utcp-kb/logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_extraction(self, selective_repos: Optional[List[str]] = None):
        """Run the extraction phase"""
        self.logger.info("Starting extraction phase")
        
        cmd = [sys.executable, "utcp_kb_extractor.py"]
        if selective_repos:
            for repo in selective_repos:
                cmd.extend(["--repo", repo])
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("Extraction completed successfully")
            self.logger.debug(f"Extraction output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Extraction failed: {e}")
            self.logger.error(f"Extraction error output: {e.stderr}")
            raise
    
    def run_processing(self):
        """Run the processing phase"""
        self.logger.info("Starting processing phase")
        
        cmd = [sys.executable, "utcp_kb_processor.py"]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("Processing completed successfully")
            self.logger.debug(f"Processing output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Processing failed: {e}")
            self.logger.error(f"Processing error output: {e.stderr}")
            raise
    
    def run_ai_optimization(self):
        """Run the AI optimization phase"""
        self.logger.info("Starting AI optimization phase")
        
        cmd = [sys.executable, "utcp_kb_ai_optimizer.py"]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("AI optimization completed successfully")
            self.logger.debug(f"AI optimization output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"AI optimization failed: {e}")
            self.logger.error(f"AI optimization error output: {e.stderr}")
            raise
    
    def run_full_pipeline(self, selective_repos: Optional[List[str]] = None, 
                         skip_extraction: bool = False, skip_processing: bool = False, 
                         skip_ai_optimization: bool = False):
        """Run the full knowledge extraction pipeline"""
        self.logger.info("Starting full UTCP knowledge extraction pipeline")
        
        if not skip_extraction:
            self.run_extraction(selective_repos)
        else:
            self.logger.info("Skipping extraction phase")
        
        if not skip_processing:
            self.run_processing()
        else:
            self.logger.info("Skipping processing phase")
        
        if not skip_ai_optimization:
            self.run_ai_optimization()
        else:
            self.logger.info("Skipping AI optimization phase")
        
        self.logger.info("Completed UTCP knowledge extraction pipeline")
    
    def run_iterative_extraction(self, max_iterations: int = 3, expansion_factor: float = 1.5):
        """Run iterative extraction to expand scope and depth"""
        self.logger.info(f"Starting iterative extraction with {max_iterations} iterations")
        
        for iteration in range(max_iterations):
            self.logger.info(f"Starting iteration {iteration + 1}")
            
            # For now, we'll just run a full extraction in each iteration
            # In a more sophisticated system, we would expand the scope/depth based on previous results
            self.run_extraction()
            
            # Update the configuration for next iteration if needed
            # This could involve increasing depth, expanding scope, etc.
            
            self.logger.info(f"Completed iteration {iteration + 1}")
        
        # After iterative extraction, process and optimize
        self.run_processing()
        self.run_ai_optimization()
    
    def update_knowledge_base(self, selective_repos: Optional[List[str]] = None):
        """Update the knowledge base with new information"""
        self.logger.info("Starting knowledge base update")
        
        # For updates, we might want to only process specific repositories
        if selective_repos:
            self.run_extraction(selective_repos)
            self.run_processing()
            self.run_ai_optimization()
        else:
            # Full update
            self.run_full_pipeline()
    
    def create_knowledge_api(self):
        """Create a simple API for accessing the knowledge base"""
        api_content = '''
#!/usr/bin/env python3
"""
Simple API for accessing the UTCP knowledge base
"""

from flask import Flask, jsonify, request
import json
from pathlib import Path

app = Flask(__name__)

# Load knowledge base data
def load_data(file_path):
    """Load JSON data from a file"""
    path = Path(file_path)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "UTCP Knowledge API"})

@app.route('/concepts', methods=['GET'])
def get_concepts():
    """Get all concepts"""
    concepts = load_data('.utcp-kb/processed-knowledge/concepts/all_concepts.json')
    return jsonify(concepts)

@app.route('/concepts/search', methods=['GET'])
def search_concepts():
    """Search for concepts by name or type"""
    query = request.args.get('q', '').lower()
    concept_type = request.args.get('type', '')
    
    concepts = load_data('.utcp-kb/processed-knowledge/concepts/all_concepts.json')
    
    filtered = []
    for concept in concepts:
        if query and query not in concept['name'].lower() and query not in concept['description'].lower():
            continue
        if concept_type and concept_type != concept['type']:
            continue
        filtered.append(concept)
    
    return jsonify(filtered)

@app.route('/relationships', methods=['GET'])
def get_relationships():
    """Get all relationships"""
    relationships = load_data('.utcp-kb/processed-knowledge/relationships/all_relationships.json')
    return jsonify(relationships)

@app.route('/repositories', methods=['GET'])
def get_repositories():
    """Get all repositories"""
    repositories = load_data('.utcp-kb/processed-knowledge/repositories/all_repositories.json')
    return jsonify(repositories)

@app.route('/wisdom', methods=['GET'])
def get_wisdom():
    """Get wisdom components"""
    wisdom = {
        'principles': load_data('.utcp-kb/wisdom/principles/all_principles.json'),
        'patterns': load_data('.utcp-kb/wisdom/patterns/all_patterns.json'),
        'best_practices': load_data('.utcp-kb/wisdom/best_practices/all_best_practices.json'),
        'insights': load_data('.utcp-kb/wisdom/insights/all_insights.json')
    }
    return jsonify(wisdom)

@app.route('/search', methods=['GET'])
def global_search():
    """Global search across all knowledge"""
    query = request.args.get('q', '').lower()
    
    results = {
        'concepts': [],
        'relationships': [],
        'repositories': [],
        'wisdom': {
            'principles': [],
            'patterns': [],
            'best_practices': [],
            'insights': []
        }
    }
    
    # Search in concepts
    concepts = load_data('.utcp-kb/processed-knowledge/concepts/all_concepts.json')
    for concept in concepts:
        if query in concept['name'].lower() or query in concept['description'].lower():
            results['concepts'].append(concept)
    
    # Search in relationships
    relationships = load_data('.utcp-kb/processed-knowledge/relationships/all_relationships.json')
    for rel in relationships:
        if query in rel['source'].lower() or query in rel['target'].lower() or query in rel['context'].lower():
            results['relationships'].append(rel)
    
    # Search in repositories
    repositories = load_data('.utcp-kb/processed-knowledge/repositories/all_repositories.json')
    for repo in repositories:
        if query in repo['name'].lower():
            results['repositories'].append(repo)
    
    # Search in wisdom components
    wisdom_components = [
        ('principles', '.utcp-kb/wisdom/principles/all_principles.json'),
        ('patterns', '.utcp-kb/wisdom/patterns/all_patterns.json'),
        ('best_practices', '.utcp-kb/wisdom/best_practices/all_best_practices.json'),
        ('insights', '.utcp-kb/wisdom/insights/all_insights.json')
    ]
    
    for category, path in wisdom_components:
        items = load_data(path)
        for item in items:
            if query in item['name'].lower() or query in item['description'].lower():
                results['wisdom'][category].append(item)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
        
        api_path = Path(".utcp-kb/api.py")
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(api_content)
        
        self.logger.info("Created knowledge API at .utcp-kb/api.py")
    
    def generate_report(self):
        """Generate a report about the current state of the knowledge base"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': self.generate_summary(),
            'statistics': self.generate_statistics()
        }
        
        report_path = Path(".utcp-kb/metadata/knowledge_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Generated knowledge report at {report_path}")
        return report
    
    def generate_summary(self):
        """Generate a summary of the knowledge base"""
        summary = {
            'extraction_summary': self.load_json_if_exists('.utcp-kb/processed-knowledge/concepts/summary.json'),
            'processing_summary': self.load_json_if_exists('.utcp-kb/processed-knowledge/relationships/summary.json'),
            'repository_summary': self.load_json_if_exists('.utcp-kb/processed-knowledge/repositories/summary.json'),
            'wisdom_summary': self.load_json_if_exists('.utcp-kb/wisdom/summary.json'),
            'ai_optimization_summary': self.load_json_if_exists('.utcp-kb/ai-optimized/summaries/comprehensive_summary.json')
        }
        return summary
    
    def generate_statistics(self):
        """Generate statistics about the knowledge base"""
        stats = {
            'file_counts': {},
            'total_concepts': 0,
            'total_relationships': 0,
            'total_repositories': 0,
            'total_wisdom_items': 0
        }
        
        # Count files in each directory
        kb_dirs = [
            '.utcp-kb/raw-extractions',
            '.utcp-kb/processed-knowledge/concepts',
            '.utcp-kb/processed-knowledge/relationships',
            '.utcp-kb/processed-knowledge/repositories',
            '.utcp-kb/processed-knowledge/evolution',
            '.utcp-kb/ai-optimized/embeddings',
            '.utcp-kb/ai-optimized/indexes',
            '.utcp-kb/ai-optimized/summaries',
            '.utcp-kb/wisdom/principles',
            '.utcp-kb/wisdom/patterns',
            '.utcp-kb/wisdom/best_practices',
            '.utcp-kb/wisdom/insights',
            '.utcp-kb/metadata'
        ]
        
        for dir_path in kb_dirs:
            path = Path(dir_path)
            if path.exists():
                count = sum(1 for _ in path.rglob('*') if _.is_file())
                stats['file_counts'][dir_path] = count
        
        # Load counts from summary files
        concept_summary = self.load_json_if_exists('.utcp-kb/processed-knowledge/concepts/summary.json')
        if concept_summary:
            stats['total_concepts'] = concept_summary.get('total_concepts', 0)
        
        relationship_summary = self.load_json_if_exists('.utcp-kb/processed-knowledge/relationships/summary.json')
        if relationship_summary:
            stats['total_relationships'] = relationship_summary.get('total_relationships', 0)
        
        repo_summary = self.load_json_if_exists('.utcp-kb/processed-knowledge/repositories/summary.json')
        if repo_summary:
            stats['total_repositories'] = repo_summary.get('total_repositories', 0)
        
        wisdom_summary = self.load_json_if_exists('.utcp-kb/wisdom/summary.json')
        if wisdom_summary:
            stats['total_wisdom_items'] = (
                wisdom_summary.get('total_principles', 0) +
                wisdom_summary.get('total_patterns', 0) +
                wisdom_summary.get('total_best_practices', 0) +
                wisdom_summary.get('total_insights', 0)
            )
        
        return stats
    
    def load_json_if_exists(self, path):
        """Load JSON file if it exists, otherwise return None"""
        file_path = Path(path)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None


def main():
    """Main function to run the UTCP knowledge system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UTCP Knowledge Base System")
    parser.add_argument("action", choices=["extract", "process", "optimize", "full", "iterative", "update", "api", "report"], 
                       help="Action to perform")
    parser.add_argument("--repo", action="append", help="Specific repository to process (can be used multiple times)")
    parser.add_argument("--skip", action="append", choices=["extraction", "processing", "ai_optimization"], 
                       help="Skip specific phases of the pipeline")
    parser.add_argument("--config", default=".utcp-kb/config/extraction_config.json", 
                       help="Path to configuration file")
    
    args = parser.parse_args()
    
    system = UTCPKnowledgeSystem(config_path=args.config)
    
    if args.action == "extract":
        system.run_extraction(selective_repos=args.repo)
    elif args.action == "process":
        system.run_processing()
    elif args.action == "optimize":
        system.run_ai_optimization()
    elif args.action == "full":
        skip_extraction = "extraction" in (args.skip or [])
        skip_processing = "processing" in (args.skip or [])
        skip_ai_optimization = "ai_optimization" in (args.skip or [])
        
        system.run_full_pipeline(
            selective_repos=args.repo,
            skip_extraction=skip_extraction,
            skip_processing=skip_processing,
            skip_ai_optimization=skip_ai_optimization
        )
    elif args.action == "iterative":
        # For now, just run full pipeline, but in the future this would implement iterative expansion
        system.run_iterative_extraction()
    elif args.action == "update":
        system.update_knowledge_base(selective_repos=args.repo)
    elif args.action == "api":
        system.create_knowledge_api()
        print("Knowledge API created at .utcp-kb/api.py")
        print("To run: pip install flask && python .utcp-kb/api.py")
    elif args.action == "report":
        report = system.generate_report()
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()