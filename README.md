# Check Archive Integrity

A Python tool to check the integrity of archives in a directory. This tool can verify 7z archives, ZIP files, and multi-volume archives of both formats.

## Features

- Scans directories for 7z and ZIP archives
- Tests archive integrity using multiple methods:
  - **ZIP files**: Python's built-in `zipfile` module
  - **7z files**: py7zr Python library
  - **Multi-volume archives**: 7-Zip command-line tool (when available)
- Handles both regular archives and multi-volume/split archives:
  - 7z: `archive.7z`, `archive.7z.001`, `archive.7z.002`, etc.
  - ZIP: `archive.zip`, `archive.z01`, `archive.z02`, etc.
- Automatically detects archive types and uses the appropriate testing method
- Provides a summary of passed/failed integrity checks

## Requirements

### Required
- Python 3.9 or higher
- py7zr library (installed via requirements.txt)

### Optional (for multi-volume archives)
- 7-Zip command-line tool (`7z` or `7z.exe`)
  - **Linux/Mac**: Install via package manager (e.g., `apt install p7zip-full` or `brew install p7zip`)
  - **Windows**: Install 7-Zip from [7-zip.org](https://www.7-zip.org/)
  - **Note**: Multi-volume ZIP and 7z archives require 7-Zip to be installed

## Installation

1. Clone or download this repository
2. Install the required Python package:

```bash
pip install -r requirements.txt
```

3. (Optional) Install 7-Zip for multi-volume archive support:
   - **Ubuntu/Debian**: `sudo apt install p7zip-full`
   - **macOS**: `brew install p7zip`
   - **Windows**: Download from [7-zip.org](https://www.7-zip.org/)

## Usage

### Basic Usage

Check all archives (7z and ZIP) in a directory:
```bash
python3 main.py /path/to/directory
```

### Recursive Scanning

The tool automatically scans directories recursively by default. The `--recursive` flag is available for compatibility:

```bash
python3 main.py /path/to/directory --recursive
```

## How It Works

The tool intelligently handles different archive types:

### 1. **Regular ZIP files** (e.g., `archive.zip`)
   - Uses Python's built-in `zipfile` module
   - No external dependencies required
   - Fast and reliable for single-volume ZIP files

### 2. **Regular 7z archives** (e.g., `archive.7z`)
   - Uses py7zr library for integrity checking
   - No external dependencies required

### 3. **Multi-volume 7z archives** (e.g., `archive.7z.001`, `archive.7z.002`)
   - Automatically detected by `.7z.` pattern
   - Requires 7-Zip command-line tool
   - Tests only the first volume (`.001`)
   - 7-Zip automatically validates all volumes

### 4. **Multi-volume ZIP archives** (e.g., `archive.z01`, `archive.z02`, `archive.zip`)
   - Automatically detected by checking for `.z01`, `.z02`, etc. files
   - Requires 7-Zip command-line tool
   - Tests the final `.zip` file (or first `.z01` if no `.zip` exists)
   - 7-Zip automatically validates all volumes

## Output

The tool provides:
- Total count of archives found
- Archive type identification (ZIP, 7z, ZIP multi-volume, 7z multi-volume)
- Progress output showing which archive is being tested
- Pass/fail status for each archive (✓ for valid, ✗ for corrupted/invalid)
- A summary showing the total number of passed and failed archives
- A list of all failed archives at the end

### Example Output

```
Scanning /path/to/directory for archives (7z, ZIP, multi-volume)...
Found 4 archive(s) to test

Testing [ZIP]: /path/to/archive.zip
✓ Archive is valid

Testing [7z]: /path/to/archive.7z
✓ Archive is valid

Testing [7z multi-volume]: /path/to/split.7z.001
✓ Archive is valid

Testing [ZIP multi-volume]: /path/to/multipart.zip
✓ Archive is valid

============================================================
Summary:
  Passed: 4
  Failed: 0
============================================================
```

## Exit Codes

- `0`: All archives passed integrity checks (or no archives found)
- `1`: One or more archives failed integrity checks (or invalid directory provided)

## Supported Archive Formats

| Format | File Extension | Single Volume | Multi-Volume | Library Used |
|--------|----------------|---------------|--------------|--------------|
| ZIP | `.zip` | ✓ | ✓* | zipfile / 7-Zip |
| 7z | `.7z` | ✓ | ✓* | py7zr / 7-Zip |

\* Multi-volume support requires 7-Zip command-line tool to be installed

## Troubleshooting

### Multi-volume archives show as failed
- **Solution**: Install 7-Zip command-line tool (see Installation section)
- The tool will display a warning if 7-Zip is needed but not available

### No archives found
- Check that your archives use supported file extensions
- Verify the directory path is correct
- The tool searches recursively by default, so subdirectories are included

## Testing

The project includes a comprehensive test suite to verify all functionality.

### Test Structure

```
tests/
  fixtures/          # Test archives
  test_main.py       # Test suite
```

### Running Tests

1. Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run the test suite:
```bash
pytest tests/ -v
```

3. Run with coverage report:
```bash
pytest tests/ -v --cov=main --cov-report=term-missing
```

### Test Coverage

The test suite covers:
- Simple 7z archive integrity checking
- Simple ZIP archive integrity checking
- Multi-volume 7z archive integrity checking
- Multi-volume ZIP archive integrity checking
- Archive discovery functionality
- Corrupted archive detection
- 7z command availability detection
- Mixed archive type handling

## License

This project is provided as-is for checking archive integrity.