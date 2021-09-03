import sys, csv
from piecash import open_book, Account, Transaction, Split, ledger

TERM = "EASTER"
DUE_DATE = "2022-07-08"

book = open_book("CUSWPC.gnucash")
GBP = book.default_currency

count = 0
for team_name in ("MWP", "WWP", "P1", "Uni 2", "Uni 1"):
    with open(team_name + "_bills_to_send.csv", "w") as teamcsv:
        team_writer = csv.writer(teamcsv, lineterminator="\n")
        members = book.get(Account, name=team_name + " Members")
        for acc in members.children:
            with open("csv/%s.csv" % acc.name, "w") as csvfile:
                csvwriter = csv.writer(csvfile, lineterminator="\n")
                count += 1
                csvwriter.writerow([acc.name, acc.description, TERM, DUE_DATE])
                total = 0

                for split in sorted(acc.splits, key=lambda split: split.transaction.post_date):
                    csvwriter.writerow([split.transaction.post_date, split.transaction.description, -split.value])
                    total += -split.value

                team_writer.writerow([acc.name, acc.description, total])

print(count, "bills produced")

