"""This script categorises applications by type which Plan It may have missed"""

import sys
import csv

def simple_find(data, keywords, label):

    for row in data:
        
        description = row.get("description")
        short = description[:100].lower().replace(" ","")
        
        if any(keyword in short for keyword in keywords):
            row["app_type"] = label
            print(row["name"])

    return data

def searches(data):

    amendment_keywords = ["amendment"]
    eia_keywords = ["eia","screeningopinion","scopingopinion","environmentalimpact","regulation6","regulation15","regulation8","regulation5(6)"]
    preapplication_keywords = ["pre-application", "applicationnotice", "PAN", "PPA"]
    conditions_keywords = ["dischargeofcondition","variationofcondition","removalofcondition","approvalofdetails","detailspersuant","conditions","discharge","variation"]
    consultation_keywords = ["consultationfrom","consultationby","consultationon","outofborough","observation","neighbouring"]

    data = simple_find(data, eia_keywords, "EIA")
    data = simple_find(preapplication_keywords, "Pre-application")
    data = simple_find(data, conditions_keywords, "Conditions")
    data = simple_find(data, amendment_keywords, "Amendment")
    data = simple_find(data, consultation_keywords, "Consultation")

    return data

def main():

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, encoding="utf-8-sig", newline="") as f:
        data = list(csv.DictReader(f))

    data = searches(data)

    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

main()
