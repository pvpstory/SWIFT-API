from fastapi import FastAPI
import sqlite3
app = FastAPI()
con = sqlite3.connect("SWIFT-CODES.db")
cur = con.cursor()



@app.get("/v1/swift-codes/{swift-code}")
async def swift_codes(swift_code: str):

    cur.execute("SELECT * FROM SWIFT_CODES WHERE SWIFT_CODE = ?", (swift_code,))

    results = cur.fetchall()
    countryISO2 = results[0][0]
    swift_code = results[0][1]
    Name = results[0][2]
    address = results[0][3]
    country_name = results[0][4]
    is_headquarter = results[0][5]

    main = {
            "address": address,
            "bankName": Name,
            "countryISO2": countryISO2,
            "countryName": country_name,
            "isHeadquarter": True,
            "swiftCode": swift_code,
        }
    print(is_headquarter)
    if is_headquarter == "0":
        main["isHeadquarter"] = False
        return main

    branches_code = swift_code[:-3] + "%"
    res = cur.execute("SELECT * FROM SWIFT_CODES WHERE SWIFT_CODE LIKE ? AND ISHEADQUARTER != 1", (branches_code,))
    results = cur.fetchall()
    branches = []
    for i,bank in enumerate(results):

        countryISO2 = results[i][0]
        swift_code = results[i][1]
        Name = results[i][2]
        address = results[i][3]
        country_name = results[i][4]
        is_headquarter = results[i][5]
        new_bank = {
            "address": address,
            "bankName": Name,
            "countryISO2": countryISO2,
            "isHeadquarter": False,
            "swiftCode": swift_code,

        }
        branches.append(new_bank)
    main["branches"] = branches
    return main







@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
