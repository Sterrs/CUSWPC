#!/usr/bin/python

import jinja2
import os
import csv
import sys
from jinja2 import Template

def format_val(val):
    if val < 0:
        return "-£{:.2f}".format(abs(val))
    else:
        return " £{:.2f}".format(abs(val))

variables = { "TREASURER_NAME" : "John Doe",
              "CAM_EMAIL" : "abc123@cam.ac.uk",
              "TREASURER_EMAIL" : "example@example.com",
              "YEARS" : "20xx-yy",
              "ACCOUNT_NAME" : "CUSWPC",
              "ACCOUNT_NUMBER" : "00000000",
              "SORT_CODE" : "00-00-00",
              }

latex_jinja_env = jinja2.Environment(
	block_start_string = '\BLOCK{',
	block_end_string = '}',
	variable_start_string = '\VAR{',
	variable_end_string = '}',
	comment_start_string = '\#{',
	comment_end_string = '}',
	line_statement_prefix = '%%',
	line_comment_prefix = '%#',
	trim_blocks = True,
	autoescape = False,
	loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)

# Escape characters that will break the tex file
def sanitise(text):
    text = text.replace("\\", "\\textbackslash")
    text = text.replace("&", "\\&")
    text = text.replace("%", "\\%")
    text = text.replace("#", "\\#")
    text = text.replace("_", "\\_")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    text = text.replace("$", "\\$")
    text = text.replace("~", "\\textasciitilde")
    text = text.replace("^", "\\textasciicircum")
    return text


for filename in os.listdir("./csv"):
    csvfilename = "./csv/" + filename
    texfilename = "./tex/" + filename.split(".")[0] + ".tex"
    total = 0
    with open(csvfilename) as csvfile:
        csvreader = csv.reader(csvfile)
        NAME, _, TERM, DUE_DATE = next(csvreader)
        ENTRIES = []
        for entry in csvreader:
            amount = float(entry[2])
            total += amount
            ENTRIES.append((entry[0], sanitise(entry[1]), format_val(amount)))
    total = round(total, 2)

    if total == 0:
        credit = 0
    elif total < 0:
        credit = -1
    else:
        credit = 1

    template = latex_jinja_env.get_template('bill_template.tex')
    with open(texfilename, "w") as texfile:
        texfile.write(template.render(format_val=format_val, NAME=NAME, TERM=TERM, DUE_DATE=DUE_DATE, ENTRIES=ENTRIES,
                                      TOTAL=total, CREDIT=credit, **variables))
    print(NAME, TERM, DUE_DATE, total, credit)
    print("Converted", csvfilename, "to", texfilename)

