import sys
import mimetypes
import smtplib
import ssl
import time
import csv
from email.message import EmailMessage

if input("Are you sure you want to send people's bills out now? [y/N]") != "y":
    sys.exit(0)

def format_val(val):
    if val < 0:
        return "-£{:.2f}".format(abs(val))
    else:
        return "£{:.2f}".format(abs(val))

TERM = "Lent"
TREASURER_NAME = "Alastair Horn"
TREASURER_EMAIL = "ath35@cam.ac.uk"
YEARS = "2021-22"
ACCOUNT_NAME = "CUSWPC"
SORT_CODE = "40-16-08"
ACCOUNT_NUMBER = "32457059"
DEADLINE = "06/04/2022"

def create_email_message(member_name, member_email, total, bill_filename):
    email_content = f"""Dear {member_name},

Please find attached the breakdown of your CUSWPC {TERM} bill.\n\n"""

    if total > 0:
        email_content += f"""The club owes you {format_val(total)}.

Please reply with your account details so a refund can be issued.\n\n"""
    elif total < 0:
        email_content += f"""You owe the club {format_val(-total)}.

The payment details are as follows:

Account Name: {ACCOUNT_NAME}
Sort Code: {SORT_CODE}
Account Number: {ACCOUNT_NUMBER}

Please use your CRSid as the reference. The deadline for this payment is {DEADLINE}.\n\n"""
    else:
        email_content += f"You don't owe anything at this stage.\n\n"

    email_content += f"""If there are any queries please let me know by emailing or messaging me. My email address is {TREASURER_EMAIL}.

Best wishes,
{TREASURER_NAME}
CUSWPC Treasurer {YEARS}""" 

    msg = EmailMessage()
    msg["Subject"] = f"CUSWPC {TERM} Bill"
    msg["From"] = "CUSWPC Treasurer"
    msg["To"] = member_email
    msg.set_content(email_content)
    print(email_content + "\n")

    bill_path = "actual_bills/" + bill_filename
    print(bill_path + "\n")

    # Guess the content type based on the file's extension.
    ctype, encoding = mimetypes.guess_type(bill_path)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    with open(bill_path, 'rb') as fp:
        msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, 
                           filename=bill_filename)

    return msg

# Create a SSLContext object with default settings.
context = ssl.create_default_context()

with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.ehlo()  # Say EHLO to server
    smtp.starttls(context=context)  # Puts the connection in TLS mode.
    smtp.ehlo()

    # Attempt to log into Gmail
    number_of_tries = 3
    print('Logging into Gmail,')
    time.sleep(1)
    senders_address = "cuswpc.treasurer@gmail.com"
    print('Please type in Password, you have ' + str(number_of_tries) + ' attempts')
    access = False
    while not access:
        try:
            password = input()
            smtp.login(senders_address, password)
            access = True
        except smtplib.SMTPAuthenticationError:
            if number_of_tries > 1:
                number_of_tries = number_of_tries - 1
                print('Incorrect password please try again, you have ' + str(number_of_tries) + ' attempts left')
                access = False
            else:
                print('Too many incorrect attempts, please restart and try again')
                time.sleep(3)
                sys.exit()

    with open("bills_to_send.csv") as csvfile:
        csvreader = csv.reader(csvfile)
        for line in csvreader:
            member_name = line[0]
            member_email = line[1]
            member_total = float(line[2])
            msg = create_email_message(member_name, member_email, member_total, member_name + ".pdf")
            if input(f"Would you like to send {member_name} an email using address {member_email}, with the amount {member_total}? [y/N]") == "y":
                print("I've currently disabled email sending to prevent accidental emails")
                # smtp.send_message(msg)
            else:
                print("Okay skipping...")

 
