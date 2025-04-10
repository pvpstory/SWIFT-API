import sqlite3
import csv

con = sqlite3.connect("SWIFT-CODES.db")
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS SWIFT_CODES")
cur.execute(""" CREATE TABLE IF NOT EXISTS  SWIFT_CODES(
        COUNTRY_ISO2 TEXT,
        SWIFT_CODE TEXT PRIMARY KEY,
        NAME TEXT,
        ADDRESS TEXT,
        COUNTRY_NAME TEXT,
        ISHEADQUARTER TEXT 
    ) """)

with open("SWIFT-CODES.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        isheadquarter = False
        if row["SWIFT CODE"][-3:] == "XXX":
            isheadquarter = True
        cur.execute(
            "INSERT INTO SWIFT_CODES(COUNTRY_ISO2, SWIFT_CODE, NAME, ADDRESS, COUNTRY_NAME, ISHEADQUARTER) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                row["COUNTRY ISO2 CODE"],
                row["SWIFT CODE"],
                row["NAME"],
                row["ADDRESS"],
                row["COUNTRY NAME"],
                isheadquarter)
        )












