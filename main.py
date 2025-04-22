from fastapi import FastAPI, Depends, HTTPException
import aiosqlite
from pydantic import BaseModel
from starlette import status

app = FastAPI()


async def get_db_connection():
    async with aiosqlite.connect("SWIFT-CODES.db") as db:
        yield db


def format_bank_data(bank_row: aiosqlite.Row, is_headquarter: bool) -> dict:
    return {
        "address": bank_row[3],
        "bankName": bank_row[2],
        "countryISO2": bank_row[0].upper(),
        "countryName": bank_row[4].upper(),
        "isHeadquarter": is_headquarter,
        "swiftCode": bank_row[1],
    }
class SwiftCodeCreate(BaseModel):
    address: str
    bankName: str
    countryISO2: str
    countryName: str
    isHeadquarter: bool
    swiftCode: str



@app.get("/v1/swift-codes/{swift_code_param}")
async def get_swift_data(swift_code_param: str, db: aiosqlite.Connection = Depends(get_db_connection)):
    try:
        async with db.execute("SELECT * FROM SWIFT_CODES WHERE SWIFT_CODE = ?", (swift_code_param,)) as cursor:
            main_bank_row = await cursor.fetchone()
        if not main_bank_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"SWIFT code '{swift_code_param}' not found."
            )
        print("1")
        is_headquarter = main_bank_row[5] == "1"
        return_value = format_bank_data(main_bank_row, is_headquarter)

        if is_headquarter:
            branch_pattern = return_value["swiftCode"][:-3] + "%"
            async with await db.execute("SELECT * FROM SWIFT_CODES WHERE SWIFT_CODE LIKE ? AND ISHEADQUARTER = '0'",(branch_pattern,)) as cursor:
                branches_rows = await cursor.fetchall()
            return_value["branches"] = []
            for branch in branches_rows:
                return_value["branches"].append(format_bank_data(branch, False))
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred on the server: {e}."
        )
    return return_value


@app.get("/v1/swift-codes/country/{countryISO2code}")
async def get_swift_data_by_country(countryISO2code: str, db: aiosqlite.Connection = Depends(get_db_connection)):
    try:
        async with db.execute("SELECT * from SWIFT_CODES WHERE COUNTRY_ISO2 = ?", (countryISO2code,)) as cursor:
            results = await cursor.fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SWIFT codes found for country {countryISO2code}"
            )
        response = {
            "countryISO2": countryISO2code,
            "countryName": results[0][4],
            "swiftCodes": []
        }

        for row in results:
            country_iso = row[0]
            swift_code = row[1]
            bank_name = row[2]
            address = row[3]
            is_headquarter = row[5] == "1"

            response["swiftCodes"].append({
                "address": address,
                "bankName": bank_name,
                "countryISO2": country_iso,
                "isHeadquarter": is_headquarter,
                "swiftCode": swift_code
            })
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unexpected database error occurred during deletion: {e}"
        )

    return response


@app.post("/v1/swift-codes", status_code=status.HTTP_201_CREATED)
async def add_swift_code(
    swift_data: SwiftCodeCreate,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    print(swift_data)
    is_headquarter_db_value = "1" if swift_data.isHeadquarter else "0"

    sql_insert = """
        INSERT INTO SWIFT_CODES (
            COUNTRY_ISO2, SWIFT_CODE, NAME, ADDRESS, COUNTRY_NAME, ISHEADQUARTER
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    values = (
        swift_data.countryISO2.upper(),
        swift_data.swiftCode,
        swift_data.bankName,
        swift_data.address,
        swift_data.countryName.upper(),
        is_headquarter_db_value
    )

    try:
        await db.execute(sql_insert, values)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unexpected database error occurred: {e}"
        )
    return {"message": f"SWIFT code {swift_data.swiftCode} added successfully."}

@app.delete("/v1/swift-codes/{swift_code}")
async def delete_swift_code(
    swift_code: str,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    sql_delete = "DELETE FROM SWIFT_CODES WHERE SWIFT_CODE = ?"
    try:
        async with db.execute(sql_delete, (swift_code,)) as cursor:
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"SWIFT code '{swift_code}' not found."
                )
            else:
                await db.commit()
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unexpected database error occurred during deletion: {e}"
        )
    return {"message": f"SWIFT code '{swift_code}' deleted successfully."}