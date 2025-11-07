import os
import sys
import argparse
import subprocess
import shutil
import zipfile
from pathlib import Path
from typing import Set, Optional
import py7zr

def is_7z_available() -> bool:
    """Check if 7z command is available on the system."""
    return shutil.which('7z') is not None or shutil.which('7z.exe') is not None

def get_7z_command() -> Optional[str]:
    """Get the 7z command name for the current platform."""
    if shutil.which('7z'):
        return '7z'
    elif shutil.which('7z.exe'):
        return '7z.exe'
    return None

def test_archive_with_7z(archive_path: str) -> bool:
    """Test archive integrity using 7z command-line tool."""
    cmd = get_7z_command()
    if not cmd:
        return False

    try:
        # Run 7z test command (works for both 7z and zip formats)
        result = subprocess.run(
            [cmd, 't', archive_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        # 7z returns 0 on success
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Timeout testing archive with 7z", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error running 7z command: {e}", file=sys.stderr)
        return False

def find_archives(directory: str) -> Set[str]:
    """Find all unique archives (7z and ZIP), including split/multi-volume archives."""
    archives = set()
    seen_split_bases = set()

    # Search for 7z archives
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

    # Search for ZIP archives
    for file in Path(directory).rglob('*.zip'):
        archives.add(str(file))

    # Search for multi-volume ZIP archives (.z01, .z02, etc.)
    # Multi-volume ZIPs end with .z01, .z02, ..., .zip (the last part)
    for file in Path(directory).rglob('*.z[0-9][0-9]'):
        file_str = str(file)
        # Extract base name without extension
        base_name = file_str.rsplit('.z', 1)[0]

        # Only add if we haven't seen this base before
        # We'll test using the .zip file (last volume) if it exists
        if base_name not in seen_split_bases:
            # Look for the final .zip file for this multi-volume set
            zip_file = base_name + '.zip'
            if os.path.exists(zip_file):
                archives.add(zip_file)
                seen_split_bases.add(base_name)
            else:
                # If no .zip file exists, use the first volume (.z01)
                first_volume = base_name + '.z01'
                if os.path.exists(first_volume):
                    archives.add(first_volume)
                    seen_split_bases.add(base_name)

    return archives

def test_archive(archive_path: str) -> bool:
    """Test archive integrity. Supports 7z, ZIP, and multi-volume archives."""
    archive_lower = archive_path.lower()

    # Detect multi-volume archives (need 7z command)
    is_multivolume_7z = '.7z.' in archive_lower and archive_lower.endswith('.001')

    # Check for multi-volume ZIP by looking for .z01, .z02, etc. files
    is_multivolume_zip = False
    if archive_lower.endswith('.zip') or archive_lower.endswith('.z01'):
        # Check if any .z01, .z02, etc. files exist
        base_path = archive_path.replace('.zip', '').replace('.z01', '')
        for i in range(1, 100):
            if os.path.exists(f'{base_path}.z{i:02d}'):
                is_multivolume_zip = True
                break

    # For multi-volume archives, try 7z command first
    if is_multivolume_7z or is_multivolume_zip:
        if is_7z_available():
            return test_archive_with_7z(archive_path)
        else:
            print(f"Warning: Multi-volume archive detected but 7z command not available",
                  file=sys.stderr)
            print(f"Install 7-Zip to test multi-volume archives", file=sys.stderr)
            return False

    # Test regular ZIP files with zipfile module
    if archive_lower.endswith('.zip'):
        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                # testzip() returns None if OK, or name of first bad file
                result = zf.testzip()
                return result is None
        except zipfile.BadZipFile:
            # Try with 7z as fallback if available
            if is_7z_available():
                return test_archive_with_7z(archive_path)
            return False
        except Exception as e:
            print(f"Error testing ZIP archive: {e}", file=sys.stderr)
            # Try with 7z as fallback if available
            if is_7z_available():
                return test_archive_with_7z(archive_path)
            return False

    # Test 7z files with py7zr
    if '.7z' in archive_lower:
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
            print(f"Error testing 7z archive: {e}", file=sys.stderr)
            return False

    # Unknown format
    print(f"Warning: Unknown archive format: {archive_path}", file=sys.stderr)
    return False

def main():
    parser = argparse.ArgumentParser(
        description='Check integrity of archives (7z and ZIP) in a directory'
    )
    parser.add_argument('directory', help='Directory to scan for archive files')
    parser.add_argument('--recursive', '-r', action='store_true',
                        help='Scan directory recursively (enabled by default)')
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory")
        return 1

    print(f"Scanning {args.directory} for archives (7z, ZIP, multi-volume)...")
    archives = find_archives(args.directory)

    if not archives:
        print("No archives found")
        return 0

    print(f"Found {len(archives)} archive(s) to test\n")

    results = {'passed': [], 'failed': []}

    for archive in sorted(archives):
        # Determine archive type for display
        archive_lower = archive.lower()
        if '.7z.' in archive_lower and archive_lower.endswith('.001'):
            archive_type = "7z multi-volume"
        elif archive_lower.endswith('.zip') and any(
            os.path.exists(archive.replace('.zip', f'.z{i:02d}')) for i in range(1, 10)
        ):
            archive_type = "ZIP multi-volume"
        elif archive_lower.endswith('.zip'):
            archive_type = "ZIP"
        elif '.7z' in archive_lower:
            archive_type = "7z"
        else:
            archive_type = "unknown"

        print(f"Testing [{archive_type}]: {archive}")
        if test_archive(archive):
            results['passed'].append(archive)
            print("✓ Archive is valid\n")
        else:
            results['failed'].append(archive)
            print("✗ Archive is corrupted or invalid\n")

    print("=" * 60)
    print("Summary:")
    print(f"  Passed: {len(results['passed'])}")
    print(f"  Failed: {len(results['failed'])}")
    print("=" * 60)

    if results['failed']:
        print("\nFailed archives:")
        for archive in results['failed']:
            print(f"  - {archive}")
        return 1
    return 0

if __name__ == '__main__':
    exit(main())