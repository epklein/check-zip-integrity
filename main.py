import os
import sys
import argparse
from pathlib import Path
from typing import Set
import py7zr

def find_7z_files(directory: str) -> Set[str]:
    """Find all unique 7z archives, including split volumes."""
    archives = set()
    seen_split_bases = set()
    
    for file in Path(directory).rglob('*.7z*'):
        file_str = str(file)
        
        # Check if this is a split volume (e.g., n.7z.001, n.7z.002)
        if '.7z.' in file_str:
            # Extract base name (e.g., "n.7z" from "n.7z.001")
            base_name = file_str.rsplit('.', 1)[0]
            
            # Only test the first volume (.001) of split archives
            # Skip subsequent volumes (.002, .003, etc.)
            if file_str.endswith('.001'):
                archives.add(file_str)
                seen_split_bases.add(base_name)
            # Otherwise skip this volume (we already have the first one)
        else:
            # Regular archive (e.g., a.7z), use it directly
            archives.add(file_str)
    
    return archives

def test_archive(archive_path: str) -> bool:
    """Test a 7z archive's integrity using py7zr library."""
    try:
        with py7zr.SevenZipFile(archive_path, 'r') as archive:
            # testzip() returns None if archive is OK, or name of first bad file
            result = archive.testzip()
            return result is None
    except py7zr.exceptions.Bad7zFile:
        # Invalid or corrupted 7z file
        return False
    except Exception as e:
        # Handle other potential errors (permissions, file not found, etc.)
        print(f"Error testing archive: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Check integrity of 7z archives in a directory')
    parser.add_argument('directory', help='Directory to scan for 7z files')
    parser.add_argument('--recursive', '-r', action='store_true', 
                        help='Scan directory recursively')
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory")
        return 1

    print(f"Scanning {args.directory}...")
    archives = find_7z_files(args.directory)

    if not archives:
        print("No 7z archives found")
        return 0

    results = {'passed': [], 'failed': []}

    for archive in sorted(archives):
        print(f"\nTesting: {archive}")
        if test_archive(archive):
            results['passed'].append(archive)
            print("✓ Archive is valid")
        else:
            results['failed'].append(archive)
            print("✗ Archive is corrupted or invalid")

    print("\nSummary:")
    print(f"Passed: {len(results['passed'])}")
    print(f"Failed: {len(results['failed'])}")

    if results['failed']:
        print("\nFailed archives:")
        for archive in results['failed']:
            print(f"- {archive}")
        return 1
    return 0

if __name__ == '__main__':
    exit(main())