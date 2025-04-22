import pytest
from main import format_bank_data

class MockRow(tuple):
    pass

@pytest.mark.asyncio
async def test_format_bank_data_headquarter():
    mock_row_data = MockRow(("US", "TESTUSNYCHQ", "Test Bank HQ", "1 Wall St", "United States", "1"))
    expected = {
        "address": "1 Wall St",
        "bankName": "Test Bank HQ",
        "countryISO2": "US",
        "countryName": "UNITED STATES",
        "isHeadquarter": True,
        "swiftCode": "TESTUSNYCHQ",
    }
    result = format_bank_data(mock_row_data, True)
    assert result == expected

@pytest.mark.asyncio
async def test_format_bank_data_branch():
    mock_row_data = MockRow(("GB", "TESTGBLONBR", "Test Bank Branch", "1 London Rd", "United Kingdom", "0"))
    expected = {
        "address": "1 London Rd",
        "bankName": "Test Bank Branch",
        "countryISO2": "GB",
        "countryName": "UNITED KINGDOM",
        "isHeadquarter": False,
        "swiftCode": "TESTGBLONBR",
    }
    result = format_bank_data(mock_row_data, False)
    assert result == expected

@pytest.mark.asyncio
async def test_format_bank_data_country_case():
    mock_row_data = MockRow(("de", "TESTDEFFM", "Test Bank DE", "1 Main St", "germany", "1"))
    expected = {
        "address": "1 Main St",
        "bankName": "Test Bank DE",
        "countryISO2": "DE",
        "countryName": "GERMANY",
        "isHeadquarter": True,
        "swiftCode": "TESTDEFFM",
    }
    result = format_bank_data(mock_row_data, True)
    assert result == expected