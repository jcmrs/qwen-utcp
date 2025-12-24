#!/usr/bin/env python3
"""
Basic UTCP Knowledge Extractor
Simple implementation without external dependencies beyond Python standard library
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import subprocess
import sys


def is_git_repo(path: Path) -> bool:
    """Check if a path is a git repository"""
    return (path / '.git').exists()


def get_repo_info(repo_path: Path) -> Dict[str, str]:
    """Get basic info about a git repository"""
    try:
        # Get the latest commit hash
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'], 
            cwd=repo_path, 
            capture_output=True, 
            text=True,
            check=True
        )
        commit_hash = result.stdout.strip()
        
        # Get the commit date
        result = subprocess.run(
            ['git', 'show', '-s', '--format=%ct', 'HEAD'], 
            cwd=repo_path, 
            capture_output=True, 
            text=True,
            check=True
        )
        commit_timestamp = result.stdout.strip()
        
        return {
            'commit_hash': commit_hash,
            'commit_timestamp': commit_timestamp
        }
    except:
        return {
            'commit_hash': 'unknown',
            'commit_timestamp': str(int(datetime.now().timestamp()))
        }


def scan_repository(repo_path: Path, supported_extensions: List[str]) -> List[Path]:
    """Scan a repository and return list of relevant files to extract from"""
    relevant_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip .git directories and other hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            file_path = Path(root) / file
            
            # Check if file type is supported
            if file_path.suffix.lower() in supported_extensions:
                relevant_files.append(file_path)
    
    return relevant_files


def extract_content_basic(file_path: Path) -> Dict[str, Any]:
    """Basic content extraction without complex NLP"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Basic content analysis
        lines = content.split('\n')
        line_count = len(lines)
        word_count = len([w for w in content.split() if w.strip()])
        
        # Identify content type based on file extension
        suffix = file_path.suffix.lower()
        if suffix in ['.md', '.rst']:
            content_type = 'documentation'
        elif suffix in ['.py', '.ts', '.js', '.go', '.rs', '.ex']:
            content_type = 'code'
        elif suffix in ['.json', '.yaml', '.yml']:
            content_type = 'configuration'
        else:
            content_type = 'other'
        
        # Basic extraction without complex NLP
        title = extract_title_basic(content, file_path.name)
        summary = extract_summary_basic(content)
        key_terms = extract_key_terms_basic(content)
        
        return {
            'file_path': str(file_path),
            'content_type': content_type,
            'content': content,
            'line_count': line_count,
            'word_count': word_count,
            'title': title,
            'summary': summary,
            'key_terms': key_terms,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'file_path': str(file_path),
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def extract_title_basic(content: str, filename: str) -> str:
    """Extract title from content"""
    # Look for markdown or document title
    lines = content.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        if line.strip().startswith('# '):
            return line.strip()[2:].strip()
        elif line.strip().startswith('title:'):
            return line.strip()[6:].strip().strip('"\'')
    
    # Fallback to filename
    return filename.replace('_', ' ').replace('-', ' ').title()


def extract_summary_basic(content: str) -> str:
    """Extract a brief summary from content"""
    # Get first few non-empty lines as summary
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    summary_lines = []
    for line in lines:
        # Skip headers and code blocks
        if not line.startswith('#') and not line.startswith('```') and len(line) > 10:
            summary_lines.append(line)
            if len(summary_lines) >= 2:
                break
    
    summary = ' '.join(summary_lines)
    return summary[:200] + "..." if len(summary) > 200 else summary


def extract_key_terms_basic(content: str) -> List[str]:
    """Extract key terms using basic pattern matching"""
    # Look for capitalized words and common technical terms
    # This is a simplified version without complex NLP
    patterns = [
        r'\b[A-Z][a-z]{2,}[A-Z][a-z]+\b',  # CamelCase
        r'\b[A-Z]{2,}\b',  # Acronyms
        r'\b\w+-[a-z]+\b',  # hyphenated terms
        r'UTCP|API|protocol|function|class|method|interface'  # Specific terms
    ]
    
    terms = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        terms.extend(matches)
    
    # Remove duplicates and limit
    unique_terms = list(set(terms))
    return unique_terms[:20]  # Return max 20 unique terms


def extract_from_repository_basic(repo_name: str, repo_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Basic extraction from a single repository"""
    if not repo_path.exists():
        print(f"Repository {repo_name} not found at {repo_path}")
        return {}
    
    print(f"Starting basic extraction from {repo_name}")
    
    # Get git info
    repo_info = get_repo_info(repo_path)
    
    # Define supported file extensions
    supported_extensions = [
        '.md', '.rst', '.txt', '.py', '.ts', '.js', '.go', '.rs', '.ex', 
        '.json', '.yaml', '.yml', '.toml', '.cfg', '.conf'
    ]
    
    # Scan and extract from all relevant files
    relevant_files = scan_repository(repo_path, supported_extensions)
    extractions = []
    
    for file_path in relevant_files:
        print(f"  Extracting from {file_path}")
        extraction = extract_content_basic(file_path)
        extractions.append(extraction)
    
    # Organize extraction results
    repo_extraction = {
        'repository': repo_name,
        'commit_hash': repo_info['commit_hash'],
        'commit_timestamp': repo_info['commit_timestamp'],
        'file_count': len(relevant_files),
        'extractions': extractions,
        'timestamp': datetime.now().isoformat()
    }
    
    # Save extraction to the appropriate directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(repo_extraction, f, indent=2, ensure_ascii=False)
    
    print(f"Completed extraction from {repo_name}, saved to {output_file}")
    
    return repo_extraction


def main():
    """Main function for basic extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Basic UTCP Knowledge Extractor")
    parser.add_argument("--repo", action="append", help="Specific repository to extract from (can be used multiple times)")
    parser.add_argument("--upstream-dir", default="UPSTREAM", help="Directory containing upstream repositories")
    parser.add_argument("--output-dir", default=".utcp-kb/raw-extractions", help="Output directory for extractions")
    
    args = parser.parse_args()
    
    upstream_path = Path(args.upstream_dir)
    output_path = Path(args.output_dir)
    
    # Get list of repositories to process
    if args.repo:
        repos_to_process = args.repo
    else:
        # Get all directories in the upstream directory
        repos_to_process = [d.name for d in upstream_path.iterdir() if d.is_dir() and is_git_repo(d)]
    
    print(f"Processing repositories: {repos_to_process}")
    
    # Process each repository
    for repo_name in repos_to_process:
        repo_path = upstream_path / repo_name
        repo_output_dir = output_path / repo_name
        
        extract_from_repository_basic(repo_name, repo_path, repo_output_dir)


if __name__ == "__main__":
    main()