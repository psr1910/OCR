from __future__ import annotations

import re
from collections.abc import Iterable

from .models import ParsedDocument


class OCRTextParser:
    """Extract common structured fields from OCR text."""

    DATE_PATTERN = re.compile(
        r"\b(?:\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b"
    )
    AMOUNT_PATTERN = re.compile(
        r"""
        (?<![\w.-])
        (?:
            (?:KRW|USD|EUR|JPY|WON|￦|₩|\$)\s*[-+]?\d[\d,]*(?:\.\d+)?
            |
            [-+]?\d[\d,]*(?:\.\d+)?\s*(?:원|달러|엔|유로|won|dollars?)
            |
            [-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?
        )
        (?![\w.-])
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
    PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:0\d{1,2})[-.\s]?\d{3,4}[-.\s]?\d{4}\b")
    BUSINESS_REGISTRATION_PATTERN = re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{5}\b")

    def parse(self, text: str) -> ParsedDocument:
        normalized = self._normalize_text(text)
        lines = [line for line in normalized.splitlines() if line]

        return ParsedDocument(
            raw_text=normalized,
            lines=lines,
            dates=self._unique(self.DATE_PATTERN.findall(normalized)),
            amounts=self._extract_amounts(normalized),
            emails=self._unique(self.EMAIL_PATTERN.findall(normalized)),
            phone_numbers=self._unique(self.PHONE_PATTERN.findall(normalized)),
            business_registration_numbers=self._unique(
                self.BUSINESS_REGISTRATION_PATTERN.findall(normalized)
            ),
            metadata={"line_count": len(lines), "character_count": len(normalized)},
        )

    def _extract_amounts(self, text: str) -> list[str]:
        matches = [match.group(0).strip() for match in self.AMOUNT_PATTERN.finditer(text)]
        return self._unique(match for match in matches if self._looks_like_amount(match))

    @staticmethod
    def _normalize_text(text: str) -> str:
        lines = [" ".join(line.strip().split()) for line in text.replace("\r\n", "\n").split("\n")]
        return "\n".join(line for line in lines if line)

    @staticmethod
    def _looks_like_amount(value: str) -> bool:
        upper_value = value.upper()
        has_currency = any(
            unit in upper_value
            for unit in ("KRW", "USD", "EUR", "JPY", "WON", "DOLLAR", "$")
        ) or any(unit in value for unit in ("원", "달러", "엔", "유로", "￦", "₩"))
        digits = re.sub(r"\D", "", value)
        has_grouped_number = "," in value and len(digits) >= 4
        return has_currency or has_grouped_number

    @staticmethod
    def _unique(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
