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

    for i,bank in enumerate(results):
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




