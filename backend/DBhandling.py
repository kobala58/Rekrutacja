from settings import db_address, db_login, db_base, db_passwd, db_port
from pymongo import MongoClient
import json

class db:
    def __init__(self):
        conn_base = "mongodb://{}:{}@{}:{}/?authSource={}&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
        client = MongoClient(conn_base.format(db_login, db_passwd, db_address, db_port, db_base))
        self.collection = client["db_g200"]

    def insetr_data(self, data):
        self.collection.table.insert_one(data)

    def read_json(self):
        with open("seats.json", "r") as seats_data:
            data = json.load(seats_data)
            for x in data["tables"]:
                test = dict()
                test = {"stolik": x}
                self.insetr_data(test["stolik"])
