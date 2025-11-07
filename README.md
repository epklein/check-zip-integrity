# Check ZIP Integrity

A Python tool to check the integrity of 7z archives in a directory. This tool can verify both regular 7z archives and split archives (multi-volume archives).

## Features

- Scans directories for 7z archives
- Tests archive integrity using the py7zr Python library
- Handles both regular archives (e.g., `archive.7z`) and split archives (e.g., `archive.7z.001`, `archive.7z.002`)
- Automatically identifies and tests only the first volume of split archives
- Provides a summary of passed/failed integrity checks

## Requirements

- Python 3.9 or higher
- py7zr library (installed via requirements.txt)

## Installation

1. Clone or download this repository
2. Install the required Python package:

```bash
pip install -r requirements.txt
```

That's it! No need to install external 7z tools.

## Usage

### Basic Usage

Check all 7z archives in a directory:
```bash
python3 main.py /path/to/directory
```

### Recursive Scanning

The tool automatically scans directories recursively by default. The `--recursive` flag is available for future compatibility but is not currently required.

```bash
python3 main.py /path/to/directory --recursive
```

## How It Works

1. **Regular Archives**: Files ending in `.7z` (e.g., `archive.7z`) are tested directly using py7zr's built-in integrity checking.

2. **Split Archives**: For multi-volume archives like `archive.7z.001`, `archive.7z.002`, etc., the tool:
   - Identifies split archives by the `.7z.` pattern in the filename
   - Tests only the first volume (`.001` file)
   - Skips subsequent volumes (`.002`, `.003`, etc.)
   - The py7zr library automatically handles split archives when given the first volume

## Output

The tool provides:
- Progress output showing which archive is being tested
- Pass/fail status for each archive (✓ for valid, ✗ for corrupted/invalid)
- A summary showing the total number of passed and failed archives
- A list of all failed archives at the end

### Example Output

```
Scanning /path/to/directory...

Testing: /path/to/archive.7z
✓ Archive is valid

Testing: /path/to/split.7z.001
✓ Archive is valid

Summary:
Passed: 2
Failed: 0
```

## Exit Codes

- `0`: All archives passed integrity checks (or no archives found)
- `1`: One or more archives failed integrity checks (or invalid directory provided)

## License

This project is provided as-is for checking 7z archive integrity.