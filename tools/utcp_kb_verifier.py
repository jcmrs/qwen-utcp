#!/usr/bin/env python3
"""
UTCP Knowledge Base Verification Tools
Tools to verify accuracy and completeness of the knowledge base against source repositories
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Set
import hashlib
import subprocess
from datetime import datetime


def get_repo_file_list(repo_path: Path) -> List[str]:
    """Get list of all files in a repository"""
    file_list = []
    for root, dirs, files in os.walk(repo_path):
        # Skip .git and other hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            file_path = Path(root) / file
            # Only include source code and documentation files
            if file_path.suffix.lower() in [
                '.py', '.ts', '.js', '.go', '.rs', '.ex', '.md', '.rst', 
                '.json', '.yaml', '.yml', '.toml', '.cfg', '.conf', '.txt'
            ]:
                file_list.append(str(file_path.relative_to(repo_path)))
    
    return file_list


def get_repo_commit_info(repo_path: Path) -> Dict[str, str]:
    """Get commit information for a repository"""
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
        
        # Get commit message
        result = subprocess.run(
            ['git', 'show', '-s', '--format=%s', 'HEAD'], 
            cwd=repo_path, 
            capture_output=True, 
            text=True,
            check=True
        )
        commit_message = result.stdout.strip()
        
        return {
            'commit_hash': commit_hash,
            'commit_timestamp': commit_timestamp,
            'commit_message': commit_message
        }
    except:
        return {
            'commit_hash': 'unknown',
            'commit_timestamp': str(int(datetime.now().timestamp())),
            'commit_message': 'unknown'
        }


def get_kb_source_info(kb_path: Path) -> Dict[str, Any]:
    """Get information about what's in the knowledge base"""
    source_info = {}
    
    # Look at raw extractions to see what was processed
    raw_extractions_path = kb_path / "raw-extractions"
    if raw_extractions_path.exists():
        for repo_dir in raw_extractions_path.iterdir():
            if repo_dir.is_dir():
                extraction_files = list(repo_dir.glob("extraction_*.json"))
                if extraction_files:
                    with open(extraction_files[0], 'r', encoding='utf-8') as f:
                        extraction = json.load(f)
                    
                    source_info[extraction['repository']] = {
                        'commit_hash': extraction.get('commit_hash', 'unknown'),
                        'file_count': extraction.get('file_count', 0),
                        'extraction_timestamp': extraction.get('timestamp', 'unknown'),
                        'processed_files': []
                    }
                    
                    # Get the list of processed files
                    for ext in extraction['extractions']:
                        if 'file_path' in ext and 'error' not in ext:
                            # Extract just the relative file path
                            file_path = Path(ext['file_path'])
                            # Remove the UPSTREAM part and repo name to get relative path
                            parts = file_path.parts
                            try:
                                # Find 'UPSTREAM' in the path and get everything after repo name
                                upstream_idx = -1
                                repo_idx = -1
                                for i, part in enumerate(parts):
                                    if part == 'UPSTREAM':
                                        upstream_idx = i
                                    elif upstream_idx != -1 and part == extraction['repository']:
                                        repo_idx = i
                                        break

                                if repo_idx != -1:
                                    # Everything after the repo name is the relative path
                                    relative_path = Path(*parts[repo_idx+1:])
                                    source_info[extraction['repository']]['processed_files'].append(str(relative_path))
                                else:
                                    # Fallback: try to get relative path directly
                                    relative_to_repo = file_path.relative_to(Path("UPSTREAM") / extraction['repository'])
                                    source_info[extraction['repository']]['processed_files'].append(str(relative_to_repo))
                            except ValueError:
                                # If we can't make it relative, just store the original path
                                source_info[extraction['repository']]['processed_files'].append(str(file_path))
    
    return source_info


def compare_repo_to_kb(repo_name: str, upstream_path: Path, kb_path: Path) -> Dict[str, Any]:
    """Compare a repository to what's in the knowledge base"""
    repo_path = upstream_path / repo_name
    
    if not repo_path.exists():
        return {
            'repo_name': repo_name,
            'error': f'Repository {repo_name} not found at {repo_path}'
        }
    
    # Get current repo state
    repo_files = set(get_repo_file_list(repo_path))
    repo_commit_info = get_repo_commit_info(repo_path)
    
    # Get knowledge base state for this repo
    kb_source_info = get_kb_source_info(kb_path)
    
    if repo_name not in kb_source_info:
        return {
            'repo_name': repo_name,
            'status': 'NOT_IN_KB',
            'repo_file_count': len(repo_files),
            'repo_commit': repo_commit_info['commit_hash'],
            'kb_commit': 'N/A',
            'missing_files': list(repo_files)
        }
    
    kb_info = kb_source_info[repo_name]
    kb_files = set(kb_info['processed_files'])
    
    # Compare commits
    commits_match = repo_commit_info['commit_hash'] == kb_info['commit_hash']
    
    # Find files that are in repo but not in KB
    missing_from_kb = repo_files - kb_files
    
    # Find files that are in KB but not in repo (might indicate deletion or different commit)
    extra_in_kb = kb_files - repo_files
    
    return {
        'repo_name': repo_name,
        'status': 'OK' if (commits_match and not missing_from_kb) else 'MISMATCH',
        'commits_match': commits_match,
        'repo_file_count': len(repo_files),
        'kb_file_count': len(kb_files),
        'repo_commit': repo_commit_info['commit_hash'],
        'kb_commit': kb_info['commit_hash'],
        'missing_from_kb': list(missing_from_kb),
        'extra_in_kb': list(extra_in_kb),
        'match_percentage': len(kb_files) / len(repo_files) * 100 if repo_files else 0
    }


def verify_all_repos(upstream_path: Path = Path("UPSTREAM"), kb_path: Path = Path(".utcp-kb")) -> List[Dict[str, Any]]:
    """Verify all repositories in the upstream directory against the knowledge base"""
    results = []
    
    # Get all repository directories in upstream
    if upstream_path.exists():
        repo_dirs = [d for d in upstream_path.iterdir() if d.is_dir()]
        
        for repo_dir in repo_dirs:
            result = compare_repo_to_kb(repo_dir.name, upstream_path, kb_path)
            results.append(result)
    
    return results


def calculate_coverage_stats(verification_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall coverage statistics"""
    total_repos = len(verification_results)
    repos_with_data = len([r for r in verification_results if r.get('status') != 'NOT_IN_KB'])
    repos_matching = len([r for r in verification_results if r.get('status') == 'OK'])
    repos_mismatched = len([r for r in verification_results if r.get('status') == 'MISMATCH'])
    
    total_repo_files = sum(r.get('repo_file_count', 0) for r in verification_results)
    total_kb_files = sum(r.get('kb_file_count', 0) for r in verification_results if 'kb_file_count' in r)
    
    overall_coverage = (total_kb_files / total_repo_files * 100) if total_repo_files > 0 else 0
    
    return {
        'total_repositories': total_repos,
        'repositories_with_data': repos_with_data,
        'repositories_matching': repos_matching,
        'repositories_mismatched': repos_mismatched,
        'total_repo_files': total_repo_files,
        'total_kb_files': total_kb_files,
        'overall_coverage_percentage': round(overall_coverage, 2),
        'completeness_score': round((repos_with_data / total_repos * 100) if total_repos > 0 else 0, 2)
    }


def run_comprehensive_verification(upstream_path: Path = Path("UPSTREAM"), kb_path: Path = Path(".utcp-kb")):
    """Run comprehensive verification of knowledge base against source repositories"""
    print("Running comprehensive verification of UTCP Knowledge Base...")
    print("=" * 60)
    
    # Verify all repositories
    results = verify_all_repos(upstream_path, kb_path)
    
    # Calculate statistics
    stats = calculate_coverage_stats(results)
    
    print(f"Verification Results:")
    print(f"  Total repositories checked: {stats['total_repositories']}")
    print(f"  Repositories with data in KB: {stats['repositories_with_data']}")
    print(f"  Repositories fully matching: {stats['repositories_matching']}")
    print(f"  Repositories with mismatches: {stats['repositories_mismatched']}")
    print(f"  Overall file coverage: {stats['overall_coverage_percentage']}%")
    print(f"  Completeness score: {stats['completeness_score']}%")
    print()
    
    # Detailed results for each repository
    for result in results:
        print(f"Repository: {result['repo_name']}")
        print(f"  Status: {result['status']}")
        
        if result['status'] == 'NOT_IN_KB':
            print(f"  Files in repo: {result.get('repo_file_count', 0)}")
            print(f"  Status: Repository not found in knowledge base")
        elif result['status'] == 'MISMATCH':
            print(f"  Repo files: {result.get('repo_file_count', 0)}")
            print(f"  KB files: {result.get('kb_file_count', 0)}")
            print(f"  Match %: {result.get('match_percentage', 0):.2f}%")
            print(f"  Commits match: {result.get('commits_match', False)}")
            
            if result.get('missing_from_kb'):
                print(f"  Missing from KB: {len(result['missing_from_kb'])} files")
                if len(result['missing_from_kb']) <= 5:  # Show first 5 if not too many
                    for f in result['missing_from_kb'][:5]:
                        print(f"    - {f}")
                else:
                    print(f"    - (showing first 5 of {len(result['missing_from_kb'])})")
                    for f in result['missing_from_kb'][:5]:
                        print(f"    - {f}")
            
            if result.get('extra_in_kb'):
                print(f"  Extra in KB: {len(result['extra_in_kb'])} files (possible outdated)")
        else:
            print(f"  Files processed: {result.get('kb_file_count', 0)}")
            print(f"  Status: Fully processed and matching")
        
        print()
    
    print("=" * 60)
    print("Verification complete.")
    
    return {
        'results': results,
        'statistics': stats
    }


def main():
    """Main function for verification"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify UTCP Knowledge Base against source repositories")
    parser.add_argument("--upstream-path", default="UPSTREAM", help="Path to upstream repositories")
    parser.add_argument("--kb-path", default=".utcp-kb", help="Path to knowledge base")
    parser.add_argument("--repo", help="Specific repository to verify (optional)")
    
    args = parser.parse_args()
    
    if args.repo:
        # Verify specific repository
        result = compare_repo_to_kb(args.repo, Path(args.upstream_path), Path(args.kb_path))
        print(f"Verification result for {args.repo}:")
        print(json.dumps(result, indent=2))
    else:
        # Verify all repositories
        run_comprehensive_verification(Path(args.upstream_path), Path(args.kb_path))


if __name__ == "__main__":
    main()