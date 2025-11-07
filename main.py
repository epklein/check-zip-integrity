import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from typing import List, Set, Optional

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

def find_7z_executable() -> Optional[str]:
    """Find the 7z executable, handling cross-platform differences."""
    # Try common executable names
    candidates = ['7z', '7z.exe', '7za', '7za.exe']
    
    for candidate in candidates:
        exe_path = shutil.which(candidate)
        if exe_path:
            return exe_path
    
    return None

def test_archive(archive_path: str, seven_z_cmd: Optional[str] = None) -> bool:
    """Test a 7z archive's integrity using 7z command line tool."""
    if seven_z_cmd is None:
        seven_z_cmd = find_7z_executable()
        if seven_z_cmd is None:
            print("Error: 7z executable not found. Please install 7-Zip or p7zip.", file=sys.stderr)
            return False
    
    try:
        result = subprocess.run(
            [seven_z_cmd, 't', archive_path],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except subprocess.SubprocessError:
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

    # Check for 7z executable early
    seven_z_cmd = find_7z_executable()
    if seven_z_cmd is None:
        print("Error: 7z executable not found. Please install 7-Zip (Windows) or p7zip-full (Linux).", file=sys.stderr)
        print("On Windows: Download from https://www.7-zip.org/", file=sys.stderr)
        print("On Linux: Install p7zip-full package", file=sys.stderr)
        return 1

    print(f"Scanning {args.directory}...")
    archives = find_7z_files(args.directory)

    if not archives:
        print("No 7z archives found")
        return 0

    results = {'passed': [], 'failed': []}
    
    for archive in sorted(archives):
        print(f"\nTesting: {archive}")
        if test_archive(archive, seven_z_cmd):
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