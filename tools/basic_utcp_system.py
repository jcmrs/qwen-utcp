#!/usr/bin/env python3
"""
Basic UTCP Knowledge System
Simple orchestration without external dependencies
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
import subprocess
import json
from datetime import datetime


def run_command(cmd: List[str], description: str):
    """Run a command and handle errors"""
    print(f"Running: {' '.join(cmd)}")
    print(f"Description: {description}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Success: {description}")
        if result.stdout:
            print(f"Output: {result.stdout[:500]}...")  # Limit output
    except subprocess.CalledProcessError as e:
        print(f"Error in {description}: {e}")
        print(f"Error output: {e.stderr}")
        raise


def run_basic_extraction(repos: Optional[List[str]] = None, upstream_dir: str = "UPSTREAM", 
                        output_dir: str = ".utcp-kb/raw-extractions"):
    """Run basic extraction"""
    cmd = [sys.executable, "basic_utcp_extractor.py", "--output-dir", output_dir, "--upstream-dir", upstream_dir]
    
    if repos:
        for repo in repos:
            cmd.extend(["--repo", repo])
    
    run_command(cmd, "Basic UTCP Extraction")


def run_basic_processing(input_dir: str = ".utcp-kb/raw-extractions", 
                       output_dir: str = ".utcp-kb/processed-knowledge"):
    """Run basic processing"""
    cmd = [sys.executable, "basic_utcp_processor.py", "--input-dir", input_dir, "--output-dir", output_dir]
    
    run_command(cmd, "Basic UTCP Processing")


def run_basic_ai_optimization(input_dir: str = ".utcp-kb/processed-knowledge", 
                            output_dir: str = ".utcp-kb/ai-optimized"):
    """Run basic AI optimization"""
    cmd = [sys.executable, "basic_utcp_ai_optimizer.py", "--input-dir", input_dir, "--output-dir", output_dir]
    
    run_command(cmd, "Basic UTCP AI Optimization")


def run_full_pipeline(selective_repos: Optional[List[str]] = None):
    """Run the full basic pipeline"""
    print("Starting full basic UTCP knowledge pipeline...")
    
    # Create necessary directories
    Path(".utcp-kb/raw-extractions").mkdir(parents=True, exist_ok=True)
    Path(".utcp-kb/processed-knowledge").mkdir(parents=True, exist_ok=True)
    Path(".utcp-kb/ai-optimized").mkdir(parents=True, exist_ok=True)
    Path(".utcp-kb/wisdom/principles").mkdir(parents=True, exist_ok=True)
    Path(".utcp-kb/wisdom/patterns").mkdir(parents=True, exist_ok=True)
    
    # Run extraction
    run_basic_extraction(selective_repos)
    
    # Run processing
    run_basic_processing()
    
    # Run AI optimization
    run_basic_ai_optimization()
    
    print("Full basic pipeline completed!")


def main():
    """Main function for basic system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Basic UTCP Knowledge System")
    parser.add_argument("action", choices=["extract", "process", "optimize", "full", "report"], 
                       help="Action to perform")
    parser.add_argument("--repo", action="append", help="Specific repository to process (can be used multiple times)")
    parser.add_argument("--upstream-dir", default="UPSTREAM", help="Directory containing upstream repositories")
    
    args = parser.parse_args()
    
    if args.action == "extract":
        run_basic_extraction(args.repo, args.upstream_dir)
    elif args.action == "process":
        run_basic_processing()
    elif args.action == "optimize":
        run_basic_ai_optimization()
    elif args.action == "full":
        run_full_pipeline(args.repo)
    elif args.action == "report":
        # Generate a simple report
        report = generate_report()
        print(json.dumps(report, indent=2))


def generate_report():
    """Generate a basic report about the knowledge base"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'system': 'Basic UTCP Knowledge System',
        'components': {
            'raw_extractions': count_files('.utcp-kb/raw-extractions'),
            'processed_knowledge': count_files('.utcp-kb/processed-knowledge'),
            'ai_optimized': count_files('.utcp-kb/ai-optimized'),
            'wisdom': count_files('.utcp-kb/wisdom')
        },
        'status': 'operational'
    }
    return report


def count_files(directory):
    """Count files in a directory recursively"""
    path = Path(directory)
    if not path.exists():
        return 0
    return sum(1 for _ in path.rglob('*') if _.is_file())


if __name__ == "__main__":
    main()