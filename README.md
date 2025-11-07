# Check ZIP Integrity

A cross-platform Python tool to check the integrity of 7z archives in a directory. This tool can verify both regular 7z archives and split archives (multi-volume archives). Works on Windows, Linux, and macOS.

## Features

- Scans directories for 7z archives
- Tests archive integrity using the 7z command-line tool
- Handles both regular archives (e.g., `archive.7z`) and split archives (e.g., `archive.7z.001`, `archive.7z.002`)
- Automatically identifies and tests only the first volume of split archives
- Provides a summary of passed/failed integrity checks

## Requirements

- Python 3.6 or higher
- 7z command-line tool (provided by `p7zip-full` on Linux or 7-Zip on Windows)

### Installing 7z on Windows

Download and install 7-Zip from the official website:
- Visit https://www.7-zip.org/
- Download the installer for your Windows version
- During installation, make sure to add 7-Zip to your PATH, or manually add the installation directory (typically `C:\Program Files\7-Zip\`) to your system PATH

After installation, verify that `7z` is available:
```cmd
7z --help
```

### Installing p7zip-full on Linux

**Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install p7zip-full
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install p7zip-full
# or for older systems:
sudo yum install p7zip-full
```

**Arch Linux:**
```bash
sudo pacman -S p7zip-full
```

**openSUSE:**
```bash
sudo zypper install p7zip-full
```

After installation, verify that `7z` is available:
```bash
7z --help
```

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

1. **Regular Archives**: Files ending in `.7z` (e.g., `archive.7z`) are tested directly.

2. **Split Archives**: For multi-volume archives like `archive.7z.001`, `archive.7z.002`, etc., the tool:
   - Identifies split archives by the `.7z.` pattern in the filename
   - Tests only the first volume (`.001` file)
   - Skips subsequent volumes (`.002`, `.003`, etc.)
   - The `7z` command automatically handles split archives when given the first volume

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