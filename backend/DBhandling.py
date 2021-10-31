from settings import db_address, db_login, db_base, db_passwd, db_port
from pymongo import MongoClient
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json
from random import randint


class db:
    def __init__(self):
        # mongodb connect using credentials from settings.py with should be in .gitignore
        conn_base = "mongodb://{}:{}@{}:{}/?authSource={}&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
        client = MongoClient(conn_base.format(db_login, db_passwd, db_address, db_port, db_base))
        # set up proper database
        self.collection = client["db_g200"]

    # simple inserter of table
    def dataInsert(self, data):
        self.collection.table.insert_one(data)

    # used when new seats will be set
    def read_json(self):
        with open("seats.json", "r") as seats_data:
            data = json.load(seats_data)
            for x in data["tables"]:
                test = {"stolik": x}
                self.dataInsert(test["stolik"])

    # main inserter
    def insetResFromDict(self, dictData):
        insert = self.collection.reservations.insert_one(dictData)
        # item id is client-sided so after insert return item is with is used to cancel reservation
        return insert.inserted_id

    # dual purpose, all reservations on date, when seat number set return only this table
    def getReservationsFromDate(self, date, seat_number=-1):
        if type(date) == str:
            date = datetime.strptime(date, "%d %m %Y")
        # strip time to 00:00:00 to get all reservations
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        # check if seat number is set
        if seat_number != -1:
            query = {"$and": [
                {"date": {"$gte": date, "$lt": date + timedelta(days=1)}},
                {"seatNumber": seat_number}
            ]}
        else:
            query = {"date": {"$gte": date, "$lt": date + timedelta(days=1)}}
        items = self.collection.reservations.find(query)
        # need to parse ObjectID into str and make data readable
        return json.loads(json_util.dumps(items, json_options=json_util.JSONOptions(datetime_representation=2)))

    # ask DB for seat specs
    def getNumberOfSeats(self, seatNumber: int):
        item = self.collection.table.find_one({"number": seatNumber})
        resData = {
            "number": item["number"],
            "min": item["minNumberOfSeats"],
            'max': item["maxNumberOfSeats"]
        }
        return resData

    # find reservations by id to insert del code
    def find_res_by_id(self, res_id: str):
        query = {"_id": ObjectId(res_id)}
        # tricky way to make 6 digit code
        code = ''.join(str(randint(0, 9)) for _ in range(6))
        # update file with new generated del code
        self.collection.reservations.update_one(query, {"$set": {"del_code": code}})
        # return all data for given _id to send it in email
        res_data = self.collection.reservations.find_one(query)
        # if not find return False
        if res_data is not None:
            return res_data
        if res_data is None:
            return False

    # check if Reservation id AND code provided are matching
    def confirm_deleting(self, res_id: str, code_to_delete_res):
        query = {
            "$and": [{"_id": ObjectId(res_id)}, {"del_code": code_to_delete_res}]
        }
        res_data = self.collection.reservations.delete_one(query)
        if res_data.deleted_count == 1:
            return True
        else:
            return False

    def get_matching_seats(self, min_guests, date, duration):
        query = {
            "minNumberOfSeats": {"$gte": min_guests}}
        date = datetime.strptime(date, '%d/%m/%y %H:%M:%S')
        suitable_seats = self.collection.table.find(query)
        seats = []
        seat_list = []
        for x in suitable_seats:
            seat_list.append(x)
            seats.append(x["number"])
        suitable_seats = list(suitable_seats)
        print(seat_list)
        print(suitable_seats)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        reservations_query = {"$and": [
            {"date": {"$gte": date, "$lt": date + timedelta(days=1)}},
            {"seatNumber": {"$in": seats}}
        ]}
        reservations = self.collection.reservations.find(reservations_query)
        print("-------------")
        for x in reservations:
            print(x)
        seats_occ = []

        for x in reservations:
            print(x)
            start = x["date"]
            finish = start + timedelta(hours=x["duration"])
            if (date < start and date + timedelta(duration) < start) or (
                    date > finish and date + timedelta(duration) > finish):
                pass
            else:
                seats_occ.append(x["seatNumber"])
        final_seats = []
        print("Test")
        print(list(suitable_seats))
        for x in seat_list:
            print(x["number"])
            if x["number"] not in seats_occ:
                final_seats.append(x)
        return json.loads(json_util.dumps(final_seats, json_options=json_util.JSONOptions(datetime_representation=2)))
