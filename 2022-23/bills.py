import csv, sys
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
                date = datetime.strptime(date, f"%d/%m/{'%Y' if sys.platform.startswith('win') else '%y'}")
                transaction = (date, description, -round((float(amount))*100))
                teams[team_name][accname].append(transaction)

        return teams


# Generate breakdown, returning four different values, the dates, the descriptions, the amounts and the total.
def generate_breakdown(transactions):
    total = 0
    dates = []
    descriptions = []
    amounts = []

    for date, description, amount in transactions:
        dates.append(f"{date.strftime('%d/%m/%y')}")
        descriptions.append(f"{description}")
        total += amount
        amounts.append(f"{format_amount(amount)}")
    return "\n".join(dates), "\n".join(descriptions), "\n".join(amounts), round(total / 100, 2)


def write_bills(accounts, transactions):
    with open(BILLS, "w", newline="") as billsfile:
        csvwriter = csv.writer(billsfile)
        for name, items in transactions[TEAM].items():
            email = accounts[TEAM][name]
            dates, descriptions, amounts, total = generate_breakdown(items)
            csvwriter.writerow([name, email, dates, descriptions, amounts, total])
            

if __name__ == "__main__":
    accounts = read_accounts()
    transactions = read_transactions()
    write_bills(accounts, transactions)

    