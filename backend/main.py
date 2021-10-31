import json
from fastapi import FastAPI, HTTPException
from DBhandling import db
from reqestModels import CancelModels, Reservations, CancelConfirm
from email_handler import send_mail, send_mail_with_code
from datetime import datetime
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/reservations", summary="Creates a new reservation for a table.")
async def createReservation(item: Reservations):
    """
    Create an reservation with all the information:

    - **date**: Date form DD/MM/YY HH:MM:00
    - **duration**: Hours in int between <1;4>
    - **Seat number**:
    - **Full name**: Name must contain full name
    - **Phone**: 9 digit number of number in form +[10digits]
    - **Email**: valid email address
    - **Number of seats**: how many people will come with you
    """
    insert_id = db().insetResFromDict(item.dict())
    send_mail(item.dict(), insert_id)
    return JSONResponse(status_code=201, content={"reservationId": str(insert_id)})


@app.get('/reservations', summary="Returns a list of all reservations for the given date")
async def reservationsOnDate(date: str):
    date_of_res = datetime.strptime(date, '%d/%m/%y')
    reservations_from_date = db().getReservationsFromDate(date_of_res)
    return {"bookings": reservations_from_date}


@app.put("/reservations/{id}", summary="Requests a cancellation of the reservation")
async def cancelReservation(res_id: str, item: CancelModels):
    res_details = db().find_res_by_id(res_id)
    if res_details:
        time_to_reservation = res_details["date"] - datetime.now()
        if time_to_reservation < 2 * 3600:
            send_mail_with_code(dict(res_details))
            raise HTTPException(status_code=422, detail="Cannot cancel 2h before")
        else:
            return JSONResponse(status_code=200, content={"status": "Success"})

    if not res_details:
        return JSONResponse(status_code=422, content={"status": "Invalid Reservation ID"})


@app.delete('/reservations/{id}', summary="Confirms the cancellation request by hecking the verification code")
async def confirmDelete(res_id: str, item: CancelConfirm):
    info = db().confirm_deleting(res_id, item.dict()["verificationCode"])
    if info:
        JSONResponse(status_code=200, content={"status": "Success"})
    else:
        JSONResponse(status_code=422, content={"status": "Wrong code"})


@app.get("/tables", summary="Returns a list of all available tables based on the given time and number of people.")
async def tableChecker(status: str, min_seats: int, start_date: str, duration: str):
    seats = db().get_matching_seats(min_seats, start_date, duration)
    return {"tables": seats}
