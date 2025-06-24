#!/usr/bin/env python3
"""
Script to process existing issues in the repository.
"""

import sys
import argparse
from typing import List
from core.issue_processor import IssueProcessor
from config import settings


def process_issues(issue_numbers: List[int] = None, auto_apply: bool = False, state: str = "open"):
    """Process issues in the repository."""
    
    processor = IssueProcessor()
    
    try:
        if issue_numbers:
            # Process specific issues
            print(f"Processing {len(issue_numbers)} specific issues...")
            result = processor.batch_process_issues(issue_numbers, auto_apply)
        else:
            # Process all issues of specified state
            print(f"Processing all {state} issues...")
            all_issues = processor.github_service.get_all_issues(state=state)
            issue_numbers = [issue.number for issue in all_issues]
            result = processor.batch_process_issues(issue_numbers, auto_apply)
        
        # Print results
        print(f"\n📊 Processing Results:")
        print(f"Total processed: {result['total_processed']}")
        print(f"Successful: {result['successful']}")
        print(f"Failed: {result['failed']}")
        
        if result['failed'] > 0:
            print(f"\n❌ Failed issues:")
            for res in result['results']:
                if not res.get('success'):
                    print(f"  - Issue #{res.get('issue_number')}: {res.get('error')}")
        
        if result['successful'] > 0:
            print(f"\n✅ Successful issues:")
            for res in result['results']:
                if res.get('success'):
                    analysis = res.get('analysis', {})
                    print(f"  - Issue #{res.get('issue_number')}: {analysis.get('issue_type', 'unknown')} ({analysis.get('priority', 'unknown')})")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing issues: {e}")
        return None


def get_issue_stats():
    """Get repository issue statistics."""
    
    processor = IssueProcessor()
    
    try:
        stats = processor.get_processing_stats()
        
        print(f"\n📈 Repository Statistics:")
        print(f"Repository: {stats.get('repository', {}).get('full_name', 'Unknown')}")
        print(f"Total issues: {stats.get('total_issues', 0)}")
        print(f"Open issues: {stats.get('open_issues', 0)}")
        print(f"Closed issues: {stats.get('closed_issues', 0)}")
        print(f"Vector service: {'✅ Available' if stats.get('vector_service_available') else '❌ Not available'}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return None


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Process existing GitHub issues with AI analysis")
    parser.add_argument("--issues", "-i", nargs="+", type=int, help="Specific issue numbers to process")
    parser.add_argument("--auto-apply", "-a", action="store_true", help="Automatically apply AI recommendations")
    parser.add_argument("--state", "-s", choices=["open", "closed", "all"], default="open", help="Issue state to process")
    parser.add_argument("--stats", action="store_true", help="Show repository statistics only")
    
    args = parser.parse_args()
    
    print("🤖 GitHub Issue AI Agent - Issue Processor")
    print("=" * 50)
    
    if args.stats:
        get_issue_stats()
        return
    
    if args.auto_apply:
        print("⚠️  Auto-apply mode enabled - AI recommendations will be automatically applied!")
        confirm = input("Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
    
    process_issues(args.issues, args.auto_apply, args.state)


if __name__ == "__main__":
    main() 