#!/usr/bin/env python3
"""
UTCP Knowledge Base API Server
Robust API for AI assistants to access the knowledge base
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import gzip

# Try to import Flask, but provide fallback if not available
try:
    from flask import Flask, request, jsonify, Response
    flask_available = True
except ImportError:
    flask_available = False
    Flask = None


class UTCPKnowledgeBase:
    """Class to manage and access the UTCP knowledge base"""
    
    def __init__(self, kb_path: str = ".utcp-kb"):
        """Initialize with path to knowledge base directory"""
        self.kb_path = Path(kb_path)
        self._concepts = None
        self._relationships = None
        self._principles = None
        self._patterns = None
        self._indexes = {}
        self._load_indexes()
    
    def _load_json(self, subpath: str) -> Any:
        """Load a JSON file from the knowledge base"""
        file_path = self.kb_path / subpath
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _load_indexes(self):
        """Load search indexes if available"""
        try:
            indexes_path = self.kb_path / "ai-optimized" / "indexes"
            if indexes_path.exists():
                concept_index_path = indexes_path / "concept_index.json"
                relationship_index_path = indexes_path / "relationship_index.json"
                
                if concept_index_path.exists():
                    with open(concept_index_path, 'r', encoding='utf-8') as f:
                        self._indexes['concepts'] = json.load(f)
                
                if relationship_index_path.exists():
                    with open(relationship_index_path, 'r', encoding='utf-8') as f:
                        self._indexes['relationships'] = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load indexes: {e}")
    
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
    
    def search_concepts(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search concepts by name, description, or context"""
        query_lower = query.lower()
        concepts = self.get_concepts()
        results = []
        
        for concept in concepts:
            # Check if query matches in name, description, or context
            name = concept.get('name', '').lower()
            description = concept.get('description', '').lower()
            context = concept.get('context', '').lower()
            
            if (query_lower in name or 
                query_lower in description or 
                query_lower in context):
                results.append(concept)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def search_relationships(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search relationships by source, target, or context"""
        query_lower = query.lower()
        relationships = self.get_relationships()
        results = []
        
        for rel in relationships:
            source = rel.get('source', '').lower()
            target = rel.get('target', '').lower()
            context = rel.get('context', '').lower()
            
            if (query_lower in source or 
                query_lower in target or 
                query_lower in context):
                results.append(rel)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_concepts_by_repo(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get concepts from a specific repository"""
        concepts = self.get_concepts()
        return [c for c in concepts if c.get('source_repo') == repo_name]
    
    def get_concepts_by_type(self, concept_type: str) -> List[Dict[str, Any]]:
        """Get concepts of a specific type"""
        concepts = self.get_concepts()
        return [c for c in concepts if c.get('type') == concept_type]
    
    def get_relationships_by_type(self, rel_type: str) -> List[Dict[str, Any]]:
        """Get relationships of a specific type"""
        relationships = self.get_relationships()
        return [r for r in relationships if r.get('type') == rel_type]
    
    def get_concepts_by_repo_and_type(self, repo_name: str, concept_type: str) -> List[Dict[str, Any]]:
        """Get concepts from a specific repository of a specific type"""
        concepts = self.get_concepts()
        return [c for c in concepts if c.get('source_repo') == repo_name and c.get('type') == concept_type]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        return {
            'total_concepts': len(self.get_concepts()),
            'total_relationships': len(self.get_relationships()),
            'total_principles': len(self.get_principles()),
            'total_patterns': len(self.get_patterns()),
            'repositories': list(set(c['source_repo'] for c in self.get_concepts())),
            'concept_types': list(set(c['type'] for c in self.get_concepts())),
            'relationship_types': list(set(r['type'] for r in self.get_relationships())),
            'timestamp': datetime.now().isoformat()
        }


def create_api_server(kb_path: str = ".utcp-kb", host: str = "0.0.0.0", port: int = 8000):
    """Create a Flask API server for the knowledge base"""
    if not flask_available:
        print("Flask is not available. Please install it with: pip install flask")
        return None
    
    app = Flask(__name__)
    kb = UTCPKnowledgeBase(kb_path)
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy", 
            "service": "UTCP Knowledge API",
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/concepts', methods=['GET'])
    def get_all_concepts():
        """Get all concepts"""
        try:
            repo = request.args.get('repo')
            concept_type = request.args.get('type')
            
            concepts = kb.get_concepts()
            
            # Filter by repository if specified
            if repo:
                concepts = [c for c in concepts if c['source_repo'] == repo]
            
            # Filter by type if specified
            if concept_type:
                concepts = [c for c in concepts if c['type'] == concept_type]
            
            # Apply limit if specified
            limit = request.args.get('limit', type=int)
            if limit and limit > 0:
                concepts = concepts[:limit]
            
            return jsonify(concepts)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/concepts/<concept_id>', methods=['GET'])
    def get_concept_by_id(concept_id):
        """Get a specific concept by ID (index)"""
        try:
            concepts = kb.get_concepts()
            concept_id = int(concept_id)
            if 0 <= concept_id < len(concepts):
                return jsonify(concepts[concept_id])
            else:
                return jsonify({"error": "Concept not found"}), 404
        except ValueError:
            return jsonify({"error": "Invalid concept ID"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/relationships', methods=['GET'])
    def get_all_relationships():
        """Get all relationships"""
        try:
            rel_type = request.args.get('type')
            relationships = kb.get_relationships()
            
            # Filter by type if specified
            if rel_type:
                relationships = [r for r in relationships if r['type'] == rel_type]
            
            # Apply limit if specified
            limit = request.args.get('limit', type=int)
            if limit and limit > 0:
                relationships = relationships[:limit]
            
            return jsonify(relationships)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/principles', methods=['GET'])
    def get_all_principles():
        """Get all principles"""
        try:
            return jsonify(kb.get_principles())
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/patterns', methods=['GET'])
    def get_all_patterns():
        """Get all patterns"""
        try:
            return jsonify(kb.get_patterns())
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/search', methods=['GET'])
    def global_search():
        """Global search across all knowledge"""
        try:
            query = request.args.get('q', '').strip()
            if not query:
                return jsonify({"error": "Query parameter 'q' is required"}), 400
            
            limit = request.args.get('limit', default=50, type=int)
            
            results = {
                'concepts': kb.search_concepts(query, limit),
                'relationships': kb.search_relationships(query, limit),
                'principles': [],
                'patterns': []
            }
            
            # Also search in principles and patterns
            query_lower = query.lower()
            for principle in kb.get_principles():
                if query_lower in principle['name'].lower() or query_lower in principle.get('description', '').lower():
                    results['principles'].append(principle)
            
            for pattern in kb.get_patterns():
                if query_lower in pattern['name'].lower() or query_lower in pattern.get('description', '').lower():
                    results['patterns'].append(pattern)
            
            # Apply limits to principles and patterns too
            results['principles'] = results['principles'][:limit]
            results['patterns'] = results['patterns'][:limit]
            
            return jsonify(results)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/search/concepts', methods=['GET'])
    def search_concepts():
        """Search specifically in concepts"""
        try:
            query = request.args.get('q', '').strip()
            if not query:
                return jsonify({"error": "Query parameter 'q' is required"}), 400
            
            limit = request.args.get('limit', default=50, type=int)
            repo = request.args.get('repo')
            
            results = kb.search_concepts(query, limit)
            
            # Filter by repository if specified
            if repo:
                results = [c for c in results if c['source_repo'] == repo]
            
            return jsonify(results)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/repositories', methods=['GET'])
    def get_repositories():
        """Get list of repositories in the knowledge base"""
        try:
            concepts = kb.get_concepts()
            repos = list(set(c['source_repo'] for c in concepts))
            return jsonify(repos)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/stats', methods=['GET'])
    def get_stats():
        """Get statistics about the knowledge base"""
        try:
            return jsonify(kb.get_statistics())
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/', methods=['GET'])
    def api_root():
        """API root with documentation"""
        return jsonify({
            "service": "UTCP Knowledge API",
            "version": "1.0.0",
            "endpoints": {
                "GET /health": "Health check",
                "GET /concepts[?repo=repo_name&type=type&limit=n]": "Get all concepts",
                "GET /concepts/{id}": "Get concept by ID",
                "GET /relationships[?type=type&limit=n]": "Get all relationships",
                "GET /principles": "Get all principles",
                "GET /patterns": "Get all patterns",
                "GET /search?q=query[&limit=n]": "Global search",
                "GET /search/concepts?q=query[&repo=repo_name&limit=n]": "Search concepts",
                "GET /repositories": "Get list of repositories",
                "GET /stats": "Get knowledge base statistics"
            },
            "timestamp": datetime.now().isoformat()
        })
    
    return app, kb


def run_api_server(kb_path: str = ".utcp-kb", host: str = "0.0.0.0", port: int = 8000):
    """Run the API server"""
    if not flask_available:
        print("Flask is not available. Please install it with: pip install flask")
        return
    
    server_info = create_api_server(kb_path, host, port)
    if server_info is None:
        return
    
    app, kb = server_info
    
    print(f"Starting UTCP Knowledge API server...")
    print(f"Knowledge base: {kb_path}")
    print(f"Statistics: {len(kb.get_concepts())} concepts, {len(kb.get_relationships())} relationships")
    print(f"Available at: http://{host}:{port}")
    print("API endpoints:")
    print(f"  Health check: GET http://{host}:{port}/health")
    print(f"  All concepts: GET http://{host}:{port}/concepts")
    print(f"  Search: GET http://{host}:{port}/search?q=utcp")
    print(f"  Stats: GET http://{host}:{port}/stats")
    print(f"  API Docs: GET http://{host}:{port}/")
    
    app.run(host=host, port=port, debug=False)


def main():
    """Main function to run the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UTCP Knowledge Base API Server")
    parser.add_argument("--kb-path", default=".utcp-kb", help="Path to knowledge base directory")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--test", action="store_true", help="Run a simple test instead of the server")
    
    args = parser.parse_args()
    
    if args.test:
        # Run a simple test to verify the knowledge base is accessible
        print("Testing knowledge base access...")
        kb = UTCPKnowledgeBase(args.kb_path)
        
        stats = kb.get_statistics()
        print(f"Knowledge base statistics:")
        print(f"  Total concepts: {stats['total_concepts']}")
        print(f"  Total relationships: {stats['total_relationships']}")
        print(f"  Total principles: {stats['total_principles']}")
        print(f"  Total patterns: {stats['total_patterns']}")
        print(f"  Repositories: {len(stats['repositories'])}")
        
        # Test search functionality
        search_results = kb.search_concepts("utcp", limit=5)
        print(f"\\nSearch results for 'utcp' (first 5):")
        for result in search_results:
            print(f"  - {result['name']} ({result['source_repo']})")
        
        print("\\nTest completed successfully!")
    else:
        run_api_server(args.kb_path, args.host, args.port)


if __name__ == "__main__":
    main()