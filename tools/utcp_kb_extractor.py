#!/usr/bin/env python3
"""
UTCP Knowledge Base Extraction System
Main extraction engine for processing UTCP repositories
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import git
from dataclasses import dataclass


@dataclass
class ExtractionConfig:
    """Configuration for the extraction process"""
    config_path: str = ".utcp-kb/config/extraction_config.json"
    
    def __post_init__(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    @property
    def supported_file_types(self) -> List[str]:
        return self.config['extraction']['supported_file_types']
    
    @property
    def content_filters(self) -> Dict[str, bool]:
        return self.config['extraction']['content_filters']
    
    @property
    def repositories(self) -> List[str]:
        return self.config['repositories']
    
    @property
    def output_dirs(self) -> Dict[str, str]:
        return self.config['output']


class UTCPKnowledgeExtractor:
    """Main class for extracting knowledge from UTCP repositories"""
    
    def __init__(self, config_path: str = ".utcp-kb/config/extraction_config.json"):
        self.config = ExtractionConfig(config_path)
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging for the extraction process"""
        log_dir = Path(".utcp-kb/logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def scan_repository(self, repo_path: Path) -> List[Path]:
        """Scan a repository and return list of relevant files to extract from"""
        relevant_files = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directories and other hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check if file type is supported
                if file_path.suffix.lower() in self.config.supported_file_types:
                    # Check content filters
                    should_include = True
                    
                    if 'include_comments' in self.config.content_filters:
                        # For code files, we might want to extract comments
                        if file_path.suffix.lower() in ['.py', '.ts', '.js', '.go', '.rs', '.ex']:
                            should_include = self.config.content_filters['include_comments']
                    
                    if should_include:
                        relevant_files.append(file_path)
        
        return relevant_files
    
    def extract_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract content from a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Basic content analysis
            lines = content.split('\n')
            line_count = len(lines)
            word_count = len(content.split())
            
            # Identify content type based on file extension and content
            content_type = self.identify_content_type(file_path, content)
            
            # Extract key information based on content type
            extracted_info = self.extract_by_content_type(file_path, content, content_type)
            
            return {
                'file_path': str(file_path),
                'content_type': content_type,
                'content': content,
                'line_count': line_count,
                'word_count': word_count,
                'extracted_info': extracted_info,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error extracting content from {file_path}: {str(e)}")
            return {
                'file_path': str(file_path),
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def identify_content_type(self, file_path: Path, content: str) -> str:
        """Identify the content type of a file"""
        suffix = file_path.suffix.lower()
        
        # Check for specific content patterns
        if 'specification' in str(file_path).lower() or 'spec' in content.lower():
            return 'specification'
        elif 'readme' in str(file_path).lower():
            return 'documentation'
        elif 'test' in str(file_path).lower() or 'spec' in str(file_path).lower():
            return 'test'
        elif suffix in ['.py', '.ts', '.js', '.go', '.rs', '.ex']:
            return 'code'
        elif suffix in ['.md', '.rst']:
            return 'documentation'
        elif suffix in ['.json', '.yaml', '.yml']:
            return 'configuration'
        else:
            return 'other'
    
    def extract_by_content_type(self, file_path: Path, content: str, content_type: str) -> Dict[str, Any]:
        """Extract specific information based on content type"""
        extracted = {
            'title': self.extract_title(content),
            'summary': self.extract_summary(content),
            'key_terms': self.extract_key_terms(content),
            'relationships': [],
            'concepts': []
        }
        
        if content_type == 'code':
            extracted.update({
                'functions': self.extract_functions(content),
                'classes': self.extract_classes(content),
                'imports': self.extract_imports(content),
                'comments': self.extract_comments(content)
            })
        elif content_type == 'documentation':
            extracted.update({
                'sections': self.extract_sections(content),
                'examples': self.extract_examples(content)
            })
        elif content_type == 'specification':
            extracted.update({
                'spec_elements': self.extract_spec_elements(content),
                'requirements': self.extract_requirements(content)
            })
        
        return extracted
    
    def extract_title(self, content: str) -> str:
        """Extract title from content"""
        # Look for markdown or document title
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.strip().startswith('# '):
                return line.strip()[2:].strip()
            elif line.strip().startswith('title:'):
                return line.strip()[6:].strip().strip('"\'')
        return "No Title Found"
    
    def extract_summary(self, content: str) -> str:
        """Extract a brief summary from content"""
        # Get first 3 non-empty lines as summary
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        summary_lines = []
        for line in lines:
            if not line.startswith('#') and not line.startswith('```'):  # Skip headers and code blocks
                summary_lines.append(line)
                if len(summary_lines) >= 3:
                    break
        
        summary = ' '.join(summary_lines)
        return summary[:200] + "..." if len(summary) > 200 else summary
    
    def extract_key_terms(self, content: str) -> List[str]:
        """Extract key terms from content"""
        # Simple approach: find capitalized words and common technical terms
        # In a real implementation, we'd use NLP techniques
        pattern = r'\b[A-Z][a-z]{2,}\b|\b\w+-(?:protocol|api|interface|function|class|method)\b'
        matches = re.findall(pattern, content, re.IGNORECASE)
        return list(set(matches))[:20]  # Return unique terms, max 20
    
    def extract_functions(self, content: str) -> List[str]:
        """Extract function names from code content"""
        patterns = [
            r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*fn\s*\(',
            r'func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        ]
        
        functions = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            functions.extend(matches)
        
        return list(set(functions))
    
    def extract_classes(self, content: str) -> List[str]:
        """Extract class names from code content"""
        patterns = [
            r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'interface\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        ]
        
        classes = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            classes.extend(matches)
        
        return list(set(classes))
    
    def extract_imports(self, content: str) -> List[str]:
        """Extract import statements from code content"""
        patterns = [
            r'import\s+([a-zA-Z0-9_.]+)',
            r'from\s+([a-zA-Z0-9_.]+)\s+import',
            r'require\([\'"]([a-zA-Z0-9_/.-]+)[\'"]\)',
            r'use\s+([a-zA-Z0-9_::]+)'
        ]
        
        imports = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
        
        return list(set(imports))
    
    def extract_comments(self, content: str) -> List[str]:
        """Extract comments from code content"""
        # Match single-line and multi-line comments
        patterns = [
            r'//\s*(.+)',
            r'#\s*(.+)',
            r'/\*\*?\s*(.*?)\s*\*/',
            r'"""\s*(.*?)\s*"""',
            r"'''\s*(.*?)\s*'''"
        ]
        
        comments = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            comments.extend([match.strip() if isinstance(match, str) else match[0].strip() for match in matches if match])
        
        # Filter out very short comments
        comments = [c for c in comments if len(c) > 10]
        return comments
    
    def extract_sections(self, content: str) -> List[str]:
        """Extract section headers from documentation"""
        pattern = r'^#+\s+(.+)$'
        matches = re.findall(pattern, content, re.MULTILINE)
        return matches
    
    def extract_examples(self, content: str) -> List[str]:
        """Extract code examples from documentation"""
        # Look for markdown code blocks
        pattern = r'```(?:\w+\n)?(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        return [example.strip() for example in matches if len(example.strip()) > 10]
    
    def extract_spec_elements(self, content: str) -> List[str]:
        """Extract specification elements"""
        # Look for common spec patterns
        patterns = [
            r'(?:MUST|MUST NOT|SHOULD|SHOULD NOT|MAY)\s+[^.!?]*[.!?]',
            r'(?:REQUIREMENT|SPECIFICATION|DEFINITION):\s*([^\n]+)',
            r'```(?:json|yaml)?\s*\{.*?\}(?:\s*```)?',
        ]
        
        elements = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            elements.extend(matches if isinstance(matches[0], str) else [m[0] for m in matches if m])
        
        return elements
    
    def extract_requirements(self, content: str) -> List[str]:
        """Extract requirements from specification content"""
        pattern = r'(?:MUST|MUST NOT|SHOULD|SHOULD NOT|MAY|REQUIRED|RECOMMENDED)\s+[^.!?]*[.!?]'
        matches = re.findall(pattern, content, re.IGNORECASE)
        return matches
    
    def extract_from_repository(self, repo_name: str, selective: bool = False) -> Dict[str, Any]:
        """Extract knowledge from a single repository"""
        repo_path = Path("UPSTREAM") / repo_name
        
        if not repo_path.exists():
            self.logger.error(f"Repository {repo_name} not found at {repo_path}")
            return {}
        
        self.logger.info(f"Starting extraction from {repo_name}")
        
        # Initialize git repository object to get metadata
        try:
            git_repo = git.Repo(repo_path)
            commit_hash = git_repo.head.commit.hexsha
            commit_date = git_repo.head.commit.committed_date
        except:
            commit_hash = "unknown"
            commit_date = datetime.now().timestamp()
        
        # Scan and extract from all relevant files
        relevant_files = self.scan_repository(repo_path)
        extractions = []
        
        for file_path in relevant_files:
            self.logger.info(f"Extracting from {file_path}")
            extraction = self.extract_content(file_path)
            extractions.append(extraction)
        
        # Organize extraction results
        repo_extraction = {
            'repository': repo_name,
            'commit_hash': commit_hash,
            'commit_date': commit_date,
            'file_count': len(relevant_files),
            'extractions': extractions,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save raw extraction to the appropriate directory
        raw_dir = Path(f".utcp-kb/raw-extractions/{repo_name}")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = raw_dir / f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(repo_extraction, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Completed extraction from {repo_name}, saved to {output_file}")
        
        return repo_extraction
    
    def extract_all(self, selective_repos: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extract knowledge from all or selected repositories"""
        self.logger.info("Starting extraction from all repositories")
        
        target_repos = selective_repos if selective_repos else self.config.repositories
        extractions = {}
        
        for repo_name in target_repos:
            try:
                repo_extraction = self.extract_from_repository(repo_name, selective=True)
                extractions[repo_name] = repo_extraction
            except Exception as e:
                self.logger.error(f"Error extracting from {repo_name}: {str(e)}")
        
        # Save overall extraction summary
        summary = {
            'total_repositories_processed': len(target_repos),
            'repositories': list(target_repos),
            'timestamp': datetime.now().isoformat(),
            'extraction_summary': {repo: len(data.get('extractions', [])) 
                                 if data else 0 for repo, data in extractions.items()}
        }
        
        summary_file = Path(".utcp-kb/metadata/extraction_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info("Completed extraction from all repositories")
        return extractions


def main():
    """Main function to run the extraction system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UTCP Knowledge Base Extraction System")
    parser.add_argument("--repo", action="append", help="Specific repository to extract from (can be used multiple times)")
    parser.add_argument("--config", default=".utcp-kb/config/extraction_config.json", help="Path to configuration file")
    
    args = parser.parse_args()
    
    extractor = UTCPKnowledgeExtractor(config_path=args.config)
    
    if args.repo:
        # Selective extraction
        extractor.extract_all(selective_repos=args.repo)
    else:
        # Full extraction
        extractor.extract_all()


if __name__ == "__main__":
    main()