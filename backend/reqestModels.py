from pydantic import BaseModel, validator, root_validator
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
from DBhandling import db


class CancelModels(BaseModel):
    status: str

    @validator("status")
    def requestChecker(cls, v):
        if v != "requested cancellation":
            raise ValueError("Message should contain 'requested cancellation'")
        return v


class CancelConfirm(BaseModel):
    verificationCode: str

    @validator("verificationCode")
    def checkCodeMatch(cls, v):
        return v


class Reservations(BaseModel):
    date: str
    duration: int
    seatNumber: int
    fullName: str
    phone: str
    email: str
    numberOfSeats: int

    @validator('date')
    def dateValidator(cls, v):
        date_of_res = datetime.strptime(v, '%d/%m/%y %H:%M:%S')
        date_of_res_copy = date_of_res.replace(hour=10, minute=0, second=0)
        if date_of_res < datetime.now():
            raise ValueError("cannot reserve seat in past")
        if date_of_res.date() > datetime.now().date() + timedelta(weeks=10):
            raise ValueError("can only reserve 10 weeks ahead")
        if date_of_res < date_of_res_copy.replace(hour=10, minute=0, second=0):
            raise ValueError("cannot reserve seat before 10AM")
        return date_of_res

    @validator('duration')
    def dur(cls, v, values):
        if v > 4:
            raise ValueError("max reservation table is 4h")
        elif v < 1:
            raise ValueError("min reservation time is 1h")
        # if date.time()+timedelta(hours=v) > datetime.strptime("23:00:00", "%H:%M:%S").time():
        #    raise ValueError("restaurant is closing on 11PM")
        return v

    @validator('fullName')
    def fullNameChecker(cls, v):
        if ' ' not in v:
            raise ValueError("Your name needs to include space")
        return v

    @validator('email')
    def emailVal(cls, v):
        try:
            valid = validate_email(v)
            email = valid.email
            return email
        except EmailNotValidError:
            raise ValueError("Invalid email")

    # number should be like: +48123456789 -> 12char with leading + or 123456789 -> 9char
    @validator('phone')
    def phoneNumberValidator(cls, v):
        if len(v) == 12 and v[0] == '+' and str(v[1:]).isdecimal() is True:
            return v
        elif len(v) == 9 and str(v).isdecimal() is True:
            return v
        else:
            raise ValueError("Telephone number is invalid")

    @validator("numberOfSeats")
    def seatsChecker(cls, v, values):
        seat_info = db().getNumberOfSeats(values["seatNumber"])
        if seat_info["min"] <= v <= seat_info["max"]:
            return v
        else:
            raise ValueError("Cannot fit into seat")

    @root_validator(pre=False)
    def checkForRes(cls, values):
        date_of_res_attempt = values.get('date')
        date_of_res_attempt_finish = date_of_res_attempt + timedelta(hours=values.get("duration"))
        reservations = db().getReservationsFromDate(date_of_res_attempt, values.get("seatNumber"))
        for x in reservations:
            start = x["date"]
            finish = start + timedelta(hours=x["duration"])
            if (date_of_res_attempt < start and date_of_res_attempt_finish < start) or (
                    date_of_res_attempt > finish and date_of_res_attempt_finish > finish):
                pass
            else:
                raise ValueError("Cannot fit reservation on this hours")
        return values
