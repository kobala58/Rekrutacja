from settings import db_address, db_login, db_base, db_passwd, db_port
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json
from random import randint


class db:
    def __init__(self):
        conn_base = "mongodb://{}:{}@{}:{}/?authSource={}&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
        client = MongoClient(conn_base.format(db_login, db_passwd, db_address, db_port, db_base))
        self.collection = client["db_g200"]

    def dataInsert(self, data):
        self.collection.table.insert_one(data)

    def read_json(self):
        with open("seats.json", "r") as seats_data:
            data = json.load(seats_data)
            for x in data["tables"]:
                test = {"stolik": x}
                self.dataInsert(test["stolik"])

    def insetResFromDict(self, dictData):
        insert = self.collection.reservations.insert_one(dictData)
        return insert.inserted_id

    def getReservationsFromDate(self, date, seat_number=-1):
        if type(date) == str:
            date = datetime.strptime(date, "%d %m %Y")
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_fin = date + timedelta(days=1)
        if seat_number != -1:
            query = {"$and": [
                {"date": {"$gte": date, "$lt": date + timedelta(days=1)}},
                {"seatNumber": seat_number}
            ]}
        else:
            query = {"date": {"$gte": date, "$lt": date + timedelta(days=1)}}
        items = self.collection.reservations.find(query)
        return list(items)

    # ask DB for seat specs
    def getNumberOfSeats(self, seatNumber: int):
        item = self.collection.table.find_one({"number": seatNumber})
        resData = {
            "number": item["number"],
            "min": item["minNumberOfSeats"],
            'max': item["maxNumberOfSeats"]
        }
        return resData

    def find_res_by_id(self, res_id: str):
        # res = self.collection.reservations.find_one()
        query = {"_id": ObjectId(res_id)}
        code = ''.join(str(randint(0, 9)) for _ in range(6))
        self.collection.reservations.update_one(query, {"$set": {"del_code": code}})
        res_data = self.collection.reservations.find_one(query)
        if res_data is not None:
            return res_data
        if res_data is None:
            return False

    def confirm_deleting(self, res_id: str, code_to_delete_res):
        query = {"_id": ObjectId(res_id)}
        query = {
            "$and": [{"_id": ObjectId(res_id)}, {"del_code": code_to_delete_res}]
        }
        res_data = self.collection.reservations.find_one(query)
        return dict(res_data)["acknowledged"]
