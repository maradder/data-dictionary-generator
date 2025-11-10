"""Base exporter interface for data dictionary exports."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.dictionary import Dictionary
    from models.field import Field


class BaseExporter(ABC):
    """
    Abstract base class for data dictionary exporters.

    Defines the interface that all exporters must implement for
    exporting data dictionaries to various formats (Excel, CSV, JSON, etc.).
    """

    @abstractmethod
    def export_dictionary(
        self,
        dictionary: "Dictionary",
        fields: list["Field"],
        output_path: Path,
    ) -> None:
        """
        Export a data dictionary to a file.

        Args:
            dictionary: The Dictionary object containing metadata
            fields: List of Field objects to export
            output_path: Path where the export file should be saved

        Raises:
            IOError: If unable to write to the output path
            ValueError: If the data is invalid or cannot be exported
        """
        pass

    def validate_output_path(self, output_path: Path) -> None:
        """
        Validate that the output path is writable.

        Args:
            output_path: Path to validate

        Raises:
            ValueError: If the path is invalid
            PermissionError: If the path is not writable
        """
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if we can write to the directory
        if not output_path.parent.is_dir():
            raise ValueError(f"Parent directory does not exist: {output_path.parent}")

        # Check if file exists and is writable
        if output_path.exists() and not output_path.is_file():
            raise ValueError(f"Output path exists but is not a file: {output_path}")
