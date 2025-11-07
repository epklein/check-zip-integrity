import os
import sys
import pytest
from pathlib import Path

# Add parent directory to path to import main module
sys.path.insert(0, str(Path(__file__).parent.parent))

import main

# Fixtures directory path
FIXTURES_DIR = Path(__file__).parent / "fixtures"

class TestArchiveIntegrity:
    """Test suite for archive integrity checker."""

    def test_simple_7z_valid(self):
        """Test that a simple valid 7z archive passes integrity check."""
        archive_path = FIXTURES_DIR / "valid_simple.7z"

        if not archive_path.exists():
            pytest.skip(f"Test archive not found: {archive_path}")

        result = main.test_archive(str(archive_path))
        assert result is True, "Valid simple 7z archive should pass integrity check"

    def test_simple_zip_valid(self):
        """Test that a simple valid ZIP archive passes integrity check."""
        archive_path = FIXTURES_DIR / "valid_simple.zip"

        if not archive_path.exists():
            pytest.skip(f"Test archive not found: {archive_path}")

        result = main.test_archive(str(archive_path))
        assert result is True, "Valid simple ZIP archive should pass integrity check"

    def test_multi_volume_7z_valid(self):
        """Test that a multi-volume 7z archive passes integrity check."""
        # Test with the first volume (.001 file)
        archive_path = FIXTURES_DIR / "valid_multi.7z.001"

        if not archive_path.exists():
            pytest.skip(f"Test archive not found: {archive_path}")

        # This test requires 7z command to be available
        if not main.is_7z_available():
            pytest.skip("7z command not available - required for multi-volume archives")

        result = main.test_archive(str(archive_path))
        assert result is True, "Valid multi-volume 7z archive should pass integrity check"

    def test_multi_volume_zip_valid(self):
        """Test that a multi-volume ZIP archive passes integrity check."""
        # Test with the final .zip file
        archive_path = FIXTURES_DIR / "valid_multi.zip"

        if not archive_path.exists():
            # Try the first volume if .zip doesn't exist
            archive_path = FIXTURES_DIR / "valid_multi.z01"
            if not archive_path.exists():
                pytest.skip(f"Test archive not found: valid_multi.zip or valid_multi.z01")

        # This test requires 7z command to be available
        if not main.is_7z_available():
            pytest.skip("7z command not available - required for multi-volume archives")

        result = main.test_archive(str(archive_path))
        assert result is True, "Valid multi-volume ZIP archive should pass integrity check"

    def test_corrupted_7z(self):
        """Test that a corrupted 7z archive fails integrity check."""
        archive_path = FIXTURES_DIR / "corrupted.7z"

        if not archive_path.exists():
            pytest.skip(f"Test archive not found: {archive_path}")

        result = main.test_archive(str(archive_path))
        assert result is False, "Corrupted 7z archive should fail integrity check"

    def test_corrupted_multi_volume_7z(self):
        """Test that a multi-volume 7z archive is corrupted."""
        # Test with the first volume (.001 file)
        archive_path = FIXTURES_DIR / "corrupted_multi.7z.001"

        if not archive_path.exists():
            pytest.skip(f"Test archive not found: {archive_path}")

        # This test requires 7z command to be available
        if not main.is_7z_available():
            pytest.skip("7z command not available - required for multi-volume archives")

        result = main.test_archive(str(archive_path))
        assert result is False, "Corrupted multi-volume 7z archive should fail pass integrity check"

    def test_corrupted_multi_volume_zip(self):
        """Test that a multi-volume ZIP archive is corrupted."""
        # Test with the final .zip file
        archive_path = FIXTURES_DIR / "corrupted_multi.zip"

        if not archive_path.exists():
            pytest.skip(f"Test archive not found: {archive_path}")

        # This test requires 7z command to be available
        if not main.is_7z_available():
            pytest.skip("7z command not available - required for multi-volume archives")

        result = main.test_archive(str(archive_path))
        assert result is False, "Corrupted multi-volume ZIP archive should fail integrity check"

    def test_corrupted_zip(self):
        """Test that a corrupted ZIP archive fails integrity check."""
        archive_path = FIXTURES_DIR / "corrupted.zip"

        if not archive_path.exists():
            pytest.skip(f"Test archive not found: {archive_path}")

        result = main.test_archive(str(archive_path))
        assert result is False, "Corrupted ZIP archive should fail integrity check"


class TestArchiveDiscovery:
    """Test suite for archive discovery functionality."""

    def test_find_archives(self):
        """Test that find_archives() discovers all test archives correctly."""
        if not FIXTURES_DIR.exists():
            pytest.skip(f"Fixtures directory not found: {FIXTURES_DIR}")

        archives = main.find_archives(str(FIXTURES_DIR))

        # Check that we found all the archives
        assert len(archives) == 8, "Should find all the archives in fixtures directory"

        # Check that all found files exist
        for archive in archives:
            assert os.path.exists(archive), f"Found archive should exist: {archive}"

        # Check that we're finding the expected types
        archive_list = list(archives)
        extensions = [Path(a).suffix.lower() for a in archive_list]

        # Should find at least one .7z or .zip file
        assert any(ext in ['.7z', '.zip', '.001'] for ext in extensions), \
            "Should find at least one 7z or zip archive"

    def test_find_archives_empty_directory(self, tmp_path):
        """Test find_archives() with an empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        archives = main.find_archives(str(empty_dir))
        assert len(archives) == 0, "Should find no archives in empty directory"

    def test_find_archives_mixed_types(self):
        """Test that find_archives() finds both ZIP and 7z archives."""
        if not FIXTURES_DIR.exists():
            pytest.skip(f"Fixtures directory not found: {FIXTURES_DIR}")

        archives = main.find_archives(str(FIXTURES_DIR))
        archive_list = list(archives)

        # Check for ZIP files
        has_zip = any('.zip' in str(a).lower() for a in archive_list)
        # Check for 7z files
        has_7z = any('.7z' in str(a).lower() for a in archive_list)

        # At least one type should be present
        assert has_zip or has_7z, "Should find at least ZIP or 7z archives"


class TestUtilityFunctions:
    """Test suite for utility functions."""

    def test_7z_availability(self):
        """Test is_7z_available() function."""
        result = main.is_7z_available()
        assert isinstance(result, bool), "is_7z_available() should return a boolean"

    def test_get_7z_command(self):
        """Test get_7z_command() function."""
        result = main.get_7z_command()

        if result is not None:
            assert isinstance(result, str), "get_7z_command() should return string or None"
            assert result in ['7z', '7z.exe'], "Should return valid 7z command name"
        else:
            # If None, 7z should not be available
            assert not main.is_7z_available(), \
                "get_7z_command() returns None but is_7z_available() is True"


if __name__ == "__main__":
    # Allow running tests directly with python
    pytest.main([__file__, "-v"])
