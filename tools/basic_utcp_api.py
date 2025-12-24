#!/usr/bin/env python3
"""
Basic UTCP Knowledge API
Simple implementation without external dependencies beyond Python standard library
"""

import json
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re


class BasicKnowledgeAPIHandler(BaseHTTPRequestHandler):
    """Basic HTTP handler for the knowledge API"""
    
    def __init__(self, *args, **kwargs):
        self.kb_base = Path(".utcp-kb")
        super().__init__(*args, **kwargs)
    
    def load_json_file(self, file_path):
        """Load JSON data from a file"""
        path = self.kb_base / file_path
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        query_params = parse_qs(parsed_path.query)
        
        if len(path_parts) >= 1:
            endpoint = path_parts[1] if len(path_parts) > 1 else path_parts[0]
            
            if endpoint == 'health':
                self.send_json_response({"status": "healthy", "service": "Basic UTCP Knowledge API"})
                
            elif endpoint == 'concepts':
                concepts = self.load_json_file('processed-knowledge/all_concepts.json')
                
                # Apply search if query parameter is provided
                if 'q' in query_params:
                    query = query_params['q'][0].lower()
                    concepts = [c for c in concepts 
                               if query in c['name'].lower() or query in c.get('description', '').lower()]
                
                self.send_json_response(concepts)
                
            elif endpoint == 'relationships':
                relationships = self.load_json_file('processed-knowledge/all_relationships.json')
                
                # Apply search if query parameter is provided
                if 'q' in query_params:
                    query = query_params['q'][0].lower()
                    relationships = [r for r in relationships 
                                   if query in r['source'].lower() or query in r['target'].lower() or query in r.get('context', '').lower()]
                
                self.send_json_response(relationships)
                
            elif endpoint == 'wisdom':
                wisdom = {
                    'principles': self.load_json_file('wisdom/principles/all_principles.json'),
                    'patterns': self.load_json_file('wisdom/patterns/all_patterns.json')
                }
                self.send_json_response(wisdom)
                
            elif endpoint == 'search':
                query = query_params.get('q', [''])[0].lower()
                
                results = {
                    'concepts': [],
                    'relationships': [],
                    'wisdom': {
                        'principles': [],
                        'patterns': []
                    }
                }
                
                # Search in concepts
                concepts = self.load_json_file('processed-knowledge/all_concepts.json')
                for concept in concepts:
                    if query in concept['name'].lower() or query in concept.get('description', '').lower():
                        results['concepts'].append(concept)
                
                # Search in relationships
                relationships = self.load_json_file('processed-knowledge/all_relationships.json')
                for rel in relationships:
                    if (query in rel['source'].lower() or 
                        query in rel['target'].lower() or 
                        query in rel.get('context', '').lower()):
                        results['relationships'].append(rel)
                
                # Search in wisdom components
                principles = self.load_json_file('wisdom/principles/all_principles.json')
                for item in principles:
                    if query in item['name'].lower() or query in item.get('description', '').lower():
                        results['wisdom']['principles'].append(item)
                
                patterns = self.load_json_file('wisdom/patterns/all_patterns.json')
                for item in patterns:
                    if query in item['name'].lower() or query in item.get('description', '').lower():
                        results['wisdom']['patterns'].append(item)
                
                self.send_json_response(results)
                
            elif endpoint == 'summary':
                summary = {
                    'concepts': self.load_json_file('processed-knowledge/concepts_summary.json'),
                    'relationships': self.load_json_file('processed-knowledge/relationships_summary.json'),
                    'wisdom': {
                        'principles': self.load_json_file('wisdom/principles/all_principles.json'),
                        'patterns': self.load_json_file('wisdom/patterns/all_patterns.json')
                    }
                }
                self.send_json_response(summary)
                
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Endpoint not found')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')


def run_api(port=8000):
    """Run the basic knowledge API"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, BasicKnowledgeAPIHandler)
    print(f"Starting Basic UTCP Knowledge API on port {port}")
    print(f"API endpoints:")
    print(f"  GET /health - Health check")
    print(f"  GET /concepts - Get all concepts")
    print(f"  GET /concepts?q=search_term - Search concepts")
    print(f"  GET /relationships - Get all relationships")
    print(f"  GET /relationships?q=search_term - Search relationships")
    print(f"  GET /wisdom - Get wisdom components")
    print(f"  GET /search?q=search_term - Global search")
    print(f"  GET /summary - Get knowledge base summary")
    httpd.serve_forever()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Basic UTCP Knowledge API")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the API on")
    
    args = parser.parse_args()
    
    run_api(args.port)