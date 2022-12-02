import csv
from datetime import datetime

# Unused by the code, just a reminder
TEAMS = ["MWP Members", "WWP Members", "P1 Members", "Uni 1 Members", "Uni 2 Members"]

# When you run the code, it will take the Account Tree from ACCOUNT_TREE,
# and the transactions from TRANSACTIONS, and output the bills to BILLS.
# It will do this only for the team TEAM
TEAM = "MWP Members"
ACCOUNT_TREE = "accounts.csv"
TRANSACTIONS = "transactions.csv"
BILLS = "bills.csv"

def format_amount(amount):
    neg = amount < 0
    amount = abs(amount)
    return f"{'-' if neg else ' '}£{amount // 100}.{str(amount % 100).rjust(2,'0')}"

# This just gets the emails for each account
# We assume that the relevant accounts are under Liabilities:Members:TEAM_NAME:MEMBER_NAME
def read_accounts():
    with open(ACCOUNT_TREE) as accountsfile:
        csvreader = csv.reader(accountsfile)
        next(csvreader)

        teams = {}
        for _,fullaccname,accname,_,email,_,_,_,_,_,_,_ in csvreader:
            fullaccname = fullaccname.split(":")
            if len(fullaccname) == 4 and fullaccname[0] == "Liabilities" and fullaccname[1] == "Members":
                team_name = fullaccname[-2]
                if team_name not in teams:
                    teams[team_name] = {}
                teams[team_name][accname] = email
        return teams


# We assume that the relevant accounts are under Liabilities:Members:TEAM_NAME:MEMBER_NAME
def read_transactions():
    with open(TRANSACTIONS) as transactionsfile:
        csvreader = csv.reader(transactionsfile)
        next(csvreader)
        
        teams = {}
        for date,_,_,description,_,_,_,_,_,fullaccname,accname,_,amount,_,_,_ in csvreader:
            fullaccname = fullaccname.split(":")
            if date != "" and len(fullaccname) == 4 and fullaccname[0] == "Liabilities" and fullaccname[1] == "Members":
                team_name = fullaccname[-2]
                if team_name not in teams:
                    teams[team_name] = {}
                if accname not in teams[team_name]:
                    teams[team_name][accname] = []

                amount = amount.replace(",","")
                date = datetime.strptime(date, "%d/%m/%y")
                transaction = (date, description, -round((float(amount))*100))
                teams[team_name][accname].append(transaction)

        return teams


def generate_breakdown(transactions):
    longest_desc = 0
    longest_amount = 0
    total = 0
    for date, description, amount in transactions:
        total += amount
        if len(description) > longest_desc:
            longest_desc = len(description)
        amount_length = len(format_amount(amount))
        if amount_length > longest_amount:
            longest_amount = amount_length

    breakdown = "Date     Details".ljust(9 + longest_desc) + " Amount\n"
    for date, description, amount in transactions:
        breakdown += f"{date.strftime('%d/%m/%y')} {description.ljust(longest_desc)} {format_amount(amount).rjust(longest_amount)}\n"
    # Don't add total, it causes confusion
    # breakdown += f"TOTAL:".rjust(9 + longest_desc) + " " + format_amount(total).rjust(longest_amount)
    return breakdown, round(total / 100, 2)


def write_bills(accounts, transactions):
    with open(BILLS, "w") as billsfile:
        csvwriter = csv.writer(billsfile)
        for name, items in transactions[TEAM].items():
            email = accounts[TEAM][name]
            breakdown, total = generate_breakdown(items)
            csvwriter.writerow([name, email, breakdown, total])
            

if __name__ == "__main__":
    accounts = read_accounts()
    print(accounts)
    transactions = read_transactions()
    write_bills(accounts, transactions)

    