"""OCR parser package."""

from .models import ParsedDocument
from .parser import OCRTextParser

__all__ = ["OCRTextParser", "ParsedDocument"]
