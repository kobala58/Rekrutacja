import smtplib
from settings import mailtrapL, mailtrapP
from socket import gaierror


# TODO EMAIL SENDING
def send_mail(res_info: dict, item_id):
    print(item_id)
    print(res_info)
    sender = "Fancy Restaurant <fancy@restaurant.com>"
    receiver = f'{res_info["fullName"]} <{res_info["email"]}>'

    message = f"""\
    Subject: Rezerwacja
    To: {receiver}
    From: {sender}
    
    Thx for reservation,
    Info:
    Reservation id: {item_id}
    Data: {res_info['date']}
    Seat Number: {res_info['seatNumber']}"""

    with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
        server.login(mailtrapL, mailtrapP)
        server.sendmail(sender, receiver, message)


def send_mail_with_code(res_info: dict):
    sender = "Fancy Restaurant <fancy@restaurant.com>"
    receiver = f'{res_info["fullName"]} <{res_info["email"]}>'

    message = f"""\
    Subject: Reservation Canncelation
    To: {receiver}
    From: {sender}

    Thx for reservation,
    Info:
    Reservation id: {res_info["_id"]}
    Code to cancel reservation: {res_info["del_code"]}
    """

    with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
        server.login(mailtrapL, mailtrapP)
        server.sendmail(sender, receiver, message)
