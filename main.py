from fastapi import FastAPI, Depends
import aiosqlite

app = FastAPI()


async def get_db_connection():
    async with aiosqlite.connect("SWIFT-CODES.db") as db:
        yield db


def format_bank_data(bank_row: aiosqlite.Row, is_headquarter: bool) -> dict:
    return {
        "address": bank_row[3],
        "bankName": bank_row[2],
        "countryISO2": bank_row[0],
        "countryName": bank_row[4],
        "isHeadquarter": is_headquarter,
        "swiftCode": bank_row[1],
    }


@app.get("/v1/swift-codes/{swift_code_param}")
async def get_swift_data(swift_code_param: str, db: aiosqlite.Connection = Depends(get_db_connection)):
    cursor = await db.execute("SELECT * FROM SWIFT_CODES WHERE SWIFT_CODE = ?", (swift_code_param,))
    main_bank_row = await cursor.fetchone()
    print(main_bank_row)
    is_headquarter = main_bank_row[5] == "1"
    return_value = format_bank_data(main_bank_row, is_headquarter)

    if is_headquarter:
        branch_pattern = return_value["swiftCode"][:-3] + "%"
        cursor = await db.execute(
            "SELECT * FROM SWIFT_CODES WHERE SWIFT_CODE LIKE ? AND ISHEADQUARTER = '0'",
            (branch_pattern,)
        )
        branches_rows = await cursor.fetchall()
        return_value["branches"] = []
        for branch in branches_rows:
            return_value["branches"].append(format_bank_data(branch, False))
    return return_value


@app.get("/v1/swift-codes/country/{countryISO2code}")
async def say_hello(contryISO2code: str):
    print("131231231")
    cur.execute("SELECT * from SWIFT_CODES WHERE COUNTRY_ISO2 = ?", (contryISO2code,))
    results = cur.fetchall()
    response = {
        "countryISO2": contryISO2code,
        "countryName": results[0][4],
        "swiftCodes": []
    }

    for i, bank in enumerate(results):
        countryISO2 = results[i][0]
        swift_code = results[i][1]
        Name = results[i][2]
        address = results[i][3]

        isHeadquarter = True
        if results[i][5] == "0":
            isHeadquarter = False

        response["swiftCodes"].append({
            "address": address,
            "bankName": Name,
            "countryISO2": countryISO2,
            "isHeadquarter": isHeadquarter,
            "swiftCode": swift_code

        })
    return response


@app.post("/v1/swift-codes")
async def insert_swift_data(swift_data: dict):
    #make sure the data is legit later
    #maby use fastapi models?
    con = sqlite3.connect("SWIFT-CODES.db")
    cur = con.cursor()

    isheadquarter = False
    if swift_data["swiftCode"][-3:] == "XXX":
        isheadquarter = True
    print(swift_data)
    cur.execute(
        "INSERT INTO SWIFT_CODES(COUNTRY_ISO2, SWIFT_CODE, NAME, ADDRESS, COUNTRY_NAME, ISHEADQUARTER) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            swift_data["countryISO2"],
            swift_data["swiftCode"],
            swift_data["bankName"],
            swift_data["address"],
            swift_data["countryName"],
            isheadquarter)
    )

    con.commit()

    return {"message": "sukces"}
