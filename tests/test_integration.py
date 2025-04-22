# tests/test_integration.py
import pytest
from httpx import AsyncClient
import aiosqlite

# Sample data to insert/use in tests
HQ_DATA = {
    "countryISO2": "FX",
    "swiftCode": "FAKEFXFFHQX",
    "bankName": "Fake Bank HQ",
    "address": "1 Fake St",
    "countryName": "Fakeland",
    "isHeadquarter": "1",
}

BRANCH_DATA_1 = {
    "countryISO2": "FX",
    "swiftCode": "FAKEFXFFB01",
    "bankName": "Fake Bank Branch 1",
    "address": "1 Branch Ave",
    "countryName": "Fakeland",
    "isHeadquarter": "0",
}

BRANCH_DATA_2 = {
    "countryISO2": "FX",
    "swiftCode": "FAKEFXFFB02",
    "bankName": "Fake Bank Branch 2",
    "address": "2 Branch Ave",
    "countryName": "Fakeland",
    "isHeadquarter": "0",
}

OTHER_COUNTRY_DATA = {
    "countryISO2": "ZZ",
    "swiftCode": "FAKEZZZZHQX",
    "bankName": "Other Fake Bank",
    "address": "1 Other St",
    "countryName": "Otherland",
    "isHeadquarter": "1",
}


async def insert_swift_code(db: aiosqlite.Connection, data: dict):
    sql = """
        INSERT INTO SWIFT_CODES (COUNTRY_ISO2, SWIFT_CODE, NAME, ADDRESS, COUNTRY_NAME, ISHEADQUARTER)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    await db.execute(sql, (
        data["countryISO2"], data["swiftCode"], data["bankName"], data["address"],
        data["countryName"], data["isHeadquarter"]
    ))
    await db.commit()


@pytest.mark.asyncio
async def test_add_swift_code(test_client: AsyncClient, db_session: aiosqlite.Connection):
    payload = {
        "address": "123 Test Ave",
        "bankName": "Integration Test Bank",
        "countryISO2": "IT",
        "countryName": "Integration Testland",
        "isHeadquarter": True,
        "swiftCode": "TESTITIT001",
    }
    response =  test_client.post("/v1/swift-codes", json=payload)
    assert response.status_code == 201
    assert response.json() == {"message": f"SWIFT code {payload['swiftCode']} added successfully."}

    # Verify in DB
    async with db_session.execute("SELECT * FROM SWIFT_CODES WHERE SWIFT_CODE = ?", (payload['swiftCode'],)) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        assert row[0] == payload['countryISO2'].upper()
        assert row[1] == payload['swiftCode']
        assert row[2] == payload['bankName']
        assert row[5] == "1"


@pytest.mark.asyncio
async def test_add_swift_code_duplicate(test_client: AsyncClient, db_session: aiosqlite.Connection):
    await insert_swift_code(db_session, HQ_DATA)
    payload = {
        "address": HQ_DATA["address"],
        "bankName": HQ_DATA["bankName"],
        "countryISO2": HQ_DATA["countryISO2"],
        "countryName": HQ_DATA["countryName"],
        "isHeadquarter": True if HQ_DATA["isHeadquarter"] == "1" else False,
        "swiftCode": HQ_DATA["swiftCode"],
    }
    response = test_client.post("/v1/swift-codes", json=payload)
    # Expecting generic 500 because the original code doesn't catch IntegrityError specifically
    assert response.status_code == 500
    assert "unexpected database error occurred" in response.json()["detail"]
    assert "UNIQUE constraint failed" in response.json()["detail"] # Check the leaked error


@pytest.mark.asyncio
async def test_get_swift_data_hq_with_branches(test_client: AsyncClient, db_session: aiosqlite.Connection):
    await insert_swift_code(db_session, HQ_DATA)
    await insert_swift_code(db_session, BRANCH_DATA_1)
    await insert_swift_code(db_session, BRANCH_DATA_2)
    await insert_swift_code(db_session, OTHER_COUNTRY_DATA)

    response =  test_client.get(f"/v1/swift-codes/{HQ_DATA['swiftCode']}")
    assert response.status_code == 200
    data = response.json()

    assert data["swiftCode"] == HQ_DATA["swiftCode"]
    assert data["isHeadquarter"] is True
    assert data["countryISO2"] == HQ_DATA["countryISO2"].upper()
    assert data["countryName"] == HQ_DATA["countryName"].upper()
    assert "branches" in data
    assert len(data["branches"]) == 2

    branch_codes = {b["swiftCode"] for b in data["branches"]}
    assert BRANCH_DATA_1["swiftCode"] in branch_codes
    assert BRANCH_DATA_2["swiftCode"] in branch_codes

    for branch in data["branches"]:
        assert branch["isHeadquarter"] is False
        assert branch["countryISO2"] == BRANCH_DATA_1["countryISO2"].upper()


@pytest.mark.asyncio
async def test_get_swift_data_branch_only(test_client: AsyncClient, db_session: aiosqlite.Connection):
    await insert_swift_code(db_session, BRANCH_DATA_1)

    response = test_client.get(f"/v1/swift-codes/{BRANCH_DATA_1['swiftCode']}")
    assert response.status_code == 200
    data = response.json()

    assert data["swiftCode"] == BRANCH_DATA_1["swiftCode"]
    assert data["isHeadquarter"] is False
    assert "branches" not in data


@pytest.mark.asyncio
async def test_get_swift_data_not_found(test_client: AsyncClient):
    response = test_client.get("/v1/swift-codes/NONEXISTENT")
    assert response.status_code == 404
    assert response.json() == {"detail": "SWIFT code 'NONEXISTENT' not found."}


@pytest.mark.asyncio
async def test_get_swift_data_by_country(test_client: AsyncClient, db_session: aiosqlite.Connection):
    await insert_swift_code(db_session, HQ_DATA)
    await insert_swift_code(db_session, BRANCH_DATA_1)
    await insert_swift_code(db_session, OTHER_COUNTRY_DATA)

    target_country = HQ_DATA["countryISO2"]
    response = test_client.get(f"/v1/swift-codes/country/{target_country}")
    assert response.status_code == 200
    data = response.json()

    assert data["countryISO2"] == target_country
    assert data["countryName"] == HQ_DATA["countryName"]
    assert len(data["swiftCodes"]) == 2

    found_codes = {sc["swiftCode"] for sc in data["swiftCodes"]}
    assert HQ_DATA["swiftCode"] in found_codes
    assert BRANCH_DATA_1["swiftCode"] in found_codes
    assert OTHER_COUNTRY_DATA["swiftCode"] not in found_codes


@pytest.mark.asyncio
async def test_get_swift_data_by_country_not_found(test_client: AsyncClient):
    response =  test_client.get("/v1/swift-codes/country/NO")
    assert response.status_code == 404
    assert response.json() == {"detail": "No SWIFT codes found for country NO"}


@pytest.mark.asyncio
async def test_delete_swift_code(test_client: AsyncClient, db_session: aiosqlite.Connection):
    await insert_swift_code(db_session, HQ_DATA)
    swift_code_to_delete = HQ_DATA["swiftCode"]

    # Verify exists before delete
    async with db_session.execute("SELECT COUNT(*) FROM SWIFT_CODES WHERE SWIFT_CODE = ?", (swift_code_to_delete,)) as cursor:
        count = await cursor.fetchone()
        assert count[0] == 1

    response = test_client.delete(f"/v1/swift-codes/{swift_code_to_delete}")
    assert response.status_code == 200
    assert response.json() == {"message": f"SWIFT code '{swift_code_to_delete}' deleted successfully."}

    # Verify deleted from DB
    async with db_session.execute("SELECT COUNT(*) FROM SWIFT_CODES WHERE SWIFT_CODE = ?", (swift_code_to_delete,)) as cursor:
        count = await cursor.fetchone()
        assert count[0] == 0


@pytest.mark.asyncio
async def test_delete_swift_code_not_found(test_client: AsyncClient):
    response = test_client.delete("/v1/swift-codes/NONEXISTENT")
    assert response.status_code == 404
    assert response.json() == {"detail": "SWIFT code 'NONEXISTENT' not found."}