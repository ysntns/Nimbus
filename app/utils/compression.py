"""
Compression Module - File compression utilities

Supports multiple compression algorithms: gzip, bz2, lzma, zstd.
"""

import bz2
import gzip
import lzma
import shutil
from pathlib import Path
from typing import Literal, Optional

from loguru import logger

try:
    import zstandard as zstd

    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False
    logger.warning("zstd not available - install with: pip install zstandard")


CompressionType = Literal["gzip", "bz2", "lzma", "zstd", "none"]


class CompressionManager:
    """Manages file compression and decompression."""

    # Default compression levels
    DEFAULT_LEVELS = {"gzip": 6, "bz2": 9, "lzma": 6, "zstd": 3}

    def __init__(
        self, compression_type: CompressionType = "gzip", level: Optional[int] = None
    ):
        """Initialize compression manager.

        Args:
            compression_type: Type of compression to use
            level: Compression level (None = default)
        """
        self.compression_type = compression_type
        self.level = level or self.DEFAULT_LEVELS.get(compression_type, 6)

        if compression_type == "zstd" and not ZSTD_AVAILABLE:
            logger.warning("zstd not available, falling back to gzip")
            self.compression_type = "gzip"

        logger.info(
            f"Compression manager initialized: {self.compression_type} (level {self.level})"
        )

    def compress_file(
        self,
        input_file: Path,
        output_file: Optional[Path] = None,
        remove_source: bool = False,
    ) -> Path:
        """Compress a file.

        Args:
            input_file: Path to input file
            output_file: Path to output file (default: input_file + extension)
            remove_source: Remove source file after compression

        Returns:
            Path to compressed file
        """
        if self.compression_type == "none":
            return input_file

        # Determine output file
        if output_file is None:
            extension = self._get_extension()
            output_file = input_file.with_suffix(input_file.suffix + extension)

        try:
            logger.info(f"Compressing {input_file} -> {output_file}")

            # Compress based on type
            if self.compression_type == "gzip":
                self._compress_gzip(input_file, output_file)
            elif self.compression_type == "bz2":
                self._compress_bz2(input_file, output_file)
            elif self.compression_type == "lzma":
                self._compress_lzma(input_file, output_file)
            elif self.compression_type == "zstd":
                self._compress_zstd(input_file, output_file)

            # Get sizes for logging
            original_size = input_file.stat().st_size
            compressed_size = output_file.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100

            logger.info(
                f"Compression complete: {original_size} -> {compressed_size} bytes ({ratio:.1f}% reduction)"
            )

            # Remove source if requested
            if remove_source:
                input_file.unlink()
                logger.debug(f"Removed source file: {input_file}")

            return output_file

        except Exception as e:
            logger.error(f"Compression failed: {e}")
            raise

    def decompress_file(
        self,
        input_file: Path,
        output_file: Optional[Path] = None,
        remove_source: bool = False,
    ) -> Path:
        """Decompress a file.

        Args:
            input_file: Path to compressed file
            output_file: Path to output file (default: input_file without extension)
            remove_source: Remove source file after decompression

        Returns:
            Path to decompressed file
        """
        # Determine compression type from extension
        compression_type = self._detect_compression_type(input_file)

        if compression_type == "none":
            return input_file

        # Determine output file
        if output_file is None:
            output_file = self._remove_compression_extension(input_file)

        try:
            logger.info(f"Decompressing {input_file} -> {output_file}")

            # Decompress based on type
            if compression_type == "gzip":
                self._decompress_gzip(input_file, output_file)
            elif compression_type == "bz2":
                self._decompress_bz2(input_file, output_file)
            elif compression_type == "lzma":
                self._decompress_lzma(input_file, output_file)
            elif compression_type == "zstd":
                self._decompress_zstd(input_file, output_file)

            logger.info(f"Decompression complete: {output_file}")

            # Remove source if requested
            if remove_source:
                input_file.unlink()
                logger.debug(f"Removed source file: {input_file}")

            return output_file

        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            raise

    def _compress_gzip(self, input_file: Path, output_file: Path):
        """Compress file using gzip."""
        with open(input_file, "rb") as f_in:
            with gzip.open(output_file, "wb", compresslevel=self.level) as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _decompress_gzip(self, input_file: Path, output_file: Path):
        """Decompress gzip file."""
        with gzip.open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _compress_bz2(self, input_file: Path, output_file: Path):
        """Compress file using bz2."""
        with open(input_file, "rb") as f_in:
            with bz2.open(output_file, "wb", compresslevel=self.level) as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _decompress_bz2(self, input_file: Path, output_file: Path):
        """Decompress bz2 file."""
        with bz2.open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _compress_lzma(self, input_file: Path, output_file: Path):
        """Compress file using lzma."""
        with open(input_file, "rb") as f_in:
            with lzma.open(output_file, "wb", preset=self.level) as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _decompress_lzma(self, input_file: Path, output_file: Path):
        """Decompress lzma file."""
        with lzma.open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _compress_zstd(self, input_file: Path, output_file: Path):
        """Compress file using zstd."""
        if not ZSTD_AVAILABLE:
            raise ImportError("zstd not available")

        cctx = zstd.ZstdCompressor(level=self.level)

        with open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                cctx.copy_stream(f_in, f_out)

    def _decompress_zstd(self, input_file: Path, output_file: Path):
        """Decompress zstd file."""
        if not ZSTD_AVAILABLE:
            raise ImportError("zstd not available")

        dctx = zstd.ZstdDecompressor()

        with open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                dctx.copy_stream(f_in, f_out)

    def _get_extension(self) -> str:
        """Get file extension for compression type."""
        extensions = {"gzip": ".gz", "bz2": ".bz2", "lzma": ".xz", "zstd": ".zst"}
        return extensions.get(self.compression_type, "")

    def _detect_compression_type(self, file_path: Path) -> CompressionType:
        """Detect compression type from file extension."""
        suffix = file_path.suffix.lower()

        if suffix in [".gz", ".gzip"]:
            return "gzip"
        elif suffix in [".bz2", ".bzip2"]:
            return "bz2"
        elif suffix in [".xz", ".lzma"]:
            return "lzma"
        elif suffix in [".zst", ".zstd"]:
            return "zstd"
        else:
            return "none"

    def _remove_compression_extension(self, file_path: Path) -> Path:
        """Remove compression extension from file path."""
        compression_extensions = [
            ".gz",
            ".gzip",
            ".bz2",
            ".bzip2",
            ".xz",
            ".lzma",
            ".zst",
            ".zstd",
        ]

        if file_path.suffix.lower() in compression_extensions:
            return file_path.with_suffix("")
        else:
            return file_path

    @staticmethod
    def get_supported_types() -> list:
        """Get list of supported compression types."""
        types = ["gzip", "bz2", "lzma"]
        if ZSTD_AVAILABLE:
            types.append("zstd")
        types.append("none")
        return types
