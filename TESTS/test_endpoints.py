import unittest
from fastapi.testclient import TestClient
from main import app
import sqlite3



class TestInsertionEndPoints(unittest.TestCase):
    def test_valid_insertion(self):

        con = sqlite3.connect('SWIFT-CODES.db')
        cur = con.cursor()

        print("Running insertion test")
        self.client = TestClient(app)

        test_bank = {
            "address": "checkAddress",
            "bankName": "checkName",
            "countryISO2": "checkCountryISO2",
            "countryName": "checkCountryName",
            "isHeadquarter": "checkIsHeadquarter",
            "swiftCode": "checkSwiftCode",
        }
        response = self.client.post("/v1/swift-codes", json=test_bank)
        cur.execute("SELECT * FROM SWIFT_CODES WHERE SWIFT_CODE = ?", ("checkSwiftCode",))
        query_result = cur.fetchall()
        cur.execute("DElETE FROM SWIFT_CODES WHERE SWIFT_CODE = 'checkSwiftCode'")
        con.commit()
        self.assertEqual("checkAddress", query_result[0][3])

if __name__ == '__main__':
    unittest.main(verbosity=2)



