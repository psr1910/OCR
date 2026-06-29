from ocr_parser import OCRTextParser


def test_parser_extracts_common_fields():
    text = """
    거래일자: 2026-06-27
    합계: 12,300원
    이메일: buyer@example.com
    연락처: 010-1234-5678
    사업자등록번호: 123-45-67890
    """

    parsed = OCRTextParser().parse(text)

    assert parsed.dates == ["2026-06-27"]
    assert parsed.amounts == ["12,300원"]
    assert parsed.emails == ["buyer@example.com"]
    assert parsed.phone_numbers == ["010-1234-5678"]
    assert parsed.business_registration_numbers == ["123-45-67890"]
    assert parsed.metadata["line_count"] == 5


def test_parser_deduplicates_matches_preserving_order():
    text = "2026/06/27 2026/06/27 01012345678 01012345678"

    parsed = OCRTextParser().parse(text)

    assert parsed.dates == ["2026/06/27"]
    assert parsed.phone_numbers == ["01012345678"]


def test_parser_does_not_treat_dates_or_phone_numbers_as_amounts():
    text = "2026-06-27 010-1234-5678 123-45-67890"

    parsed = OCRTextParser().parse(text)

    assert parsed.amounts == []


def test_parser_extracts_currency_prefixed_amounts():
    text = "KRW 45,000 / USD 12.50 / ₩9,900"

    parsed = OCRTextParser().parse(text)

    assert parsed.amounts == ["KRW 45,000", "USD 12.50", "₩9,900"]
