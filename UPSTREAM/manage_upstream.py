#!/usr/bin/env python3
"""
Utility script for managing upstream repositories in the UPSTREAM directory.

This script helps with:
- Cloning new upstream repositories
- Updating existing upstream clones
- Checking status of upstream repositories
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


UPSTREAM_DIR = Path(__file__).parent


def clone_upstream(repo_url, name=None):
    """Clone an upstream repository to the UPSTREAM directory."""
    if not name:
        # Extract name from URL
        name = repo_url.split("/")[-1].replace(".git", "")
    
    target_dir = UPSTREAM_DIR / name
    
    if target_dir.exists():
        print(f"Error: {target_dir} already exists!")
        return False
    
    print(f"Cloning {repo_url} to {target_dir}")
    try:
        subprocess.run(["git", "clone", repo_url, str(target_dir)], check=True)
        print(f"Successfully cloned {repo_url} to {target_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return False


def update_upstream(name):
    """Update an upstream repository."""
    target_dir = UPSTREAM_DIR / name
    
    if not target_dir.exists():
        print(f"Error: {target_dir} does not exist!")
        return False
    
    print(f"Updating {target_dir}")
    try:
        result = subprocess.run(
            ["git", "pull"], 
            cwd=target_dir, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"Update output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating repository: {e}")
        return False


def list_upstream():
    """List all upstream repositories."""
    print("Upstream repositories:")
    for item in UPSTREAM_DIR.iterdir():
        if item.is_dir() and (item / ".git").exists():
            print(f"  - {item.name}")


def status_upstream(name):
    """Check the status of an upstream repository."""
    target_dir = UPSTREAM_DIR / name
    
    if not target_dir.exists():
        print(f"Error: {target_dir} does not exist!")
        return False
    
    try:
        # Check if there are uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"], 
            cwd=target_dir, 
            capture_output=True, 
            text=True
        )
        
        if result.stdout.strip():
            print(f"{name} has uncommitted changes:")
            print(result.stdout)
        else:
            print(f"{name} is clean")
            
        # Check remote status
        result = subprocess.run(
            ["git", "remote", "update"], 
            cwd=target_dir, 
            capture_output=True, 
            text=True
        )
        
        # Check if local is behind remote
        result = subprocess.run(
            ["git", "status", "-uno"], 
            cwd=target_dir, 
            capture_output=True, 
            text=True
        )
        
        if "behind" in result.stdout:
            print(f"{name} is behind upstream")
        elif "up to date" in result.stdout or "ahead" in result.stdout:
            print(f"{name} is up to date with upstream")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error checking status: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Manage upstream repositories")
    parser.add_argument("action", choices=["clone", "update", "list", "status"], 
                        help="Action to perform")
    parser.add_argument("repo", nargs="?", help="Repository name or URL")
    parser.add_argument("--name", help="Name for the upstream clone (for clone action)")
    
    args = parser.parse_args()
    
    # Ensure UPSTREAM directory exists
    UPSTREAM_DIR.mkdir(exist_ok=True)
    
    if args.action == "clone":
        if not args.repo:
            print("Error: Repository URL is required for clone action")
            sys.exit(1)
        clone_upstream(args.repo, args.name)
    elif args.action == "update":
        if not args.repo:
            print("Error: Repository name is required for update action")
            sys.exit(1)
        update_upstream(args.repo)
    elif args.action == "list":
        list_upstream()
    elif args.action == "status":
        if not args.repo:
            print("Error: Repository name is required for status action")
            sys.exit(1)
        status_upstream(args.repo)


if __name__ == "__main__":
    main()