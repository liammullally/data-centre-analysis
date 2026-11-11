"""API download tool for use with the PanIt API.
Gets 10 years of planning application results for data-centre related keywords
"""

import sys
import json
import requests
import time
import datetime

url = "https://www.planit.org.uk/api/applics/json"
headers = {"User-Agent" : "datacentre planning research, lmull004@gold.ac.uk"}

#search parameters

search_terms = '"data centre" or "data center" or datacentre or datacenter'
n_years = 10
period = f"{datetime.date.today().year - n_years}-01-01"
params = {
    "search" : search_terms,
    "start_date" : period,
    "pg_sz" : 200,
    "compress" : "true"
    }

#basic api query & error messages

def planit_query(params):

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 429:
        sys.exit ("Error 429: rate limit exceeded")
            
    if response.status_code == 403:
        sys.exit ("Error 403: source IP is blocked or invalid User-Agent header detected")

    if response.status_code == 400:
        sys.exit ("Error 400: misc")

    return response.json()

#main download

def main_search():

    data = []
    page = 1

    while True:

        params["page"] = page
        results = planit_query(params)
        total = results.get("total")

        #printing total results and pages

        if page == 1:
            print(f"{total} results over {total/200} pages.")
    
        secs_taken = results.get("secs_taken")
        batch = results.get("records", [])
        data.extend(batch)
        print(f"Page {page}. Query took {secs_taken} seconds.")

        progress = results.get("to")    

        if progress + 1 >= total:
            print("Download complete.")
            break

        else:
            page += 1
            time.sleep(60)

    return data   

#filtering to relevant data points

def refine(data):

    output_fields = [
        "name",
        "uid",
        "description",
        "area_name",
        "start_date",
        "decided_date",
        "address",
        "postcode",
        "location_x",
        "location_y",
        "link",
        "applicant_company",
        "agent_company",
        "app_state",
        "app_type",
        "n_comments"
    ]

    refined = []
    for record in data:
        row = {field: record.get(field) for field in output_fields}
        other = record.get("other_fields") or {}
        row["applicant_company"] = other.get("applicant_company")
        row["agent_company"] = other.get("agent_company")
        row["n_comments"] = other.get("n_comments")

        refined.append(row)

    return refined

#exporting as json

def export_json(data):

    timestamp = datetime.date.today()
    path = f"datacentre_applications_{timestamp}.json"

    with open(path, "w", encoding="utf-8") as f: 
        json.dump(data, f)

    print(f"Saved {len(data)} applications to {path}")

#program which uses these

def main():
    results = main_search()
    refined = refine(results)
    export_json(refined)

main()