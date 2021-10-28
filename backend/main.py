from fastapi import FastAPI
from DBhandling import db
from reqestModels import CancelModels, Reservations, CancelConfirm
from email_handler import send_mail, send_mail_with_code
from datetime import datetime
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/reservations")
async def createReservation(item: Reservations):
    insert_id = db().insetResFromDict(item.dict())
    send_mail(item.dict(), insert_id)
    return JSONResponse(status_code=201, content={"reservationId": str(insert_id)})


@app.get('/reservations')
async def reservationsOnDate(date: str):
    date_of_res = datetime.strptime(date, '%d/%m/%y')
    data = db().getReservationsFromDate(date_of_res)


@app.put("/reservations/{id}")
async def cancelReservation(res_id: str, item: CancelModels):
    res_details = db().find_res_by_id(res_id)
    if res_details:
        time_to_reservation = res_details["date"] - datetime.now()
        if time_to_reservation < 2 * 3600:
            send_mail_with_code(dict(res_details))
            return JSONResponse(status_code=422, content={"status": "Cannot cancel 2h before"})
        else:

            return JSONResponse(status_code=200, content={"status": "Success"})

    if not res_details:
        return JSONResponse(status_code=422, content={"status": "Invalid Reservation ID"})


@app.delete('/reservations/{id}')
async def confirmDelete(res_id: str, item: CancelConfirm):
    info = db().confirm_deleting(res_id, item.dict()["verificationCode"])
    if info:
        JSONResponse(status_code=200, content={"status": "Success"})
    else:
        JSONResponse(status_code=422, content={"status": "Wrong code"})


@app.get("/tables")
async def tableChecker(status: str, min_seats: int, start_date: str, duration: str):
    pass
