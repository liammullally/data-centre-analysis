"""script which converts the application csv file into an aggregated site list

Expects csv input, then outputs as both csv & json output"""

import csv
import json
import sys

def find_conflicts(site_group): #flags inconsistencies within sites for manual verification

    conflicts = []
    postcodes = {application.get("postcode") for application in site_group if application.get("postcode")}
    size = {application.get("size_sqft") for application in site_group if application.get("size_sqft")}
    power = {application.get("power_mw") for application in site_group if application.get("power_mw")}
    
    if len(postcodes) > 1:
        conflicts.append("postcode")

    if len(size) > 1:
        conflicts.append("size")

    if len(power) > 1:
        conflicts.append("power")
        
    return conflicts

def add_n_comments(site_group): # adds up comment numbers

    n_comments = None
    for application in site_group:
        n = application.get("n_comments")
        if n:
            n_comments = (n_comments or 0) + int(n)

    return n_comments

def location_pick(site_group, field): # chooses location value (address, postcode, lat, long)

    output = None
    for application in site_group:
        if not application.get(field):
            continue
        
        output = application.get(field)
        break
        
    return output

def pick_main_authority(site_group):

    authorities = {application.get("area_name") for application in site_group if application.get("area_name")}
    if len(authorities) == 1:
        
        for application in site_group:
            main_authority = application.get("area_name")
            if application.get("area_name"):
                return main_authority

    if len(authorities) > 1:

        totals = {}        
        for application in site_group:
            area_name = application.get("area_name")
            if area_name and application.get("app_type") != "Consultation":
                totals[area_name] = totals.get(area_name, 0) + 1

        if totals:
            main_authority = max(totals, key=totals.get)
            return main_authority

        for application in site_group:
            if application.get("area_name"):
                main_authority = application.get("area_name")
                return main_authority

    return ""

def simple_aggregate(site_group, field): # used for references, applicants, agents, authorities and notes

    output = set()
    for application in site_group:
        pieces = application.get(field)
        if not pieces:
            continue
    
        formatted = [trimmed.strip() for trimmed in pieces.split(";")]
        output.update(formatted)
    
    return sorted (output)

def simple_pick(site_group, field): # used for category, link, description, name, size, power 

    #prefer full, then outline, 
    for application in site_group:
        if application.get("app_type") == "Full":
            if application.get(field):
                output = application.get(field)
                return output

    for application in site_group:
        if application.get("app_type") == "Outline":
            if application.get(field):
                output = application.get(field)
                return output
            
    #otherwise pick most recent EIA, Pre-application or Condition
    site_group_list = [application for application in site_group if application.get("app_type") in ("EIA", "Pre-application", "Conditions")]
    site_group_list.sort(key=lambda application: application.get("start_date") or "", reverse=True)

    for application_copy in site_group_list:
        if application_copy.get(field):
            output = application_copy.get(field)
            return output

    for application in site_group:
        if application.get(field):
            output = application.get(field)
            return output

    return ""

def pick_state(site_group): #determine what state of development is likely to be: pre-application, in progress, pre-approved, rejected, withdrawn, unknown or approved

    not_consultation = [application for application in site_group if application.get("app_type") != "Consultation"]

    if not_consultation and all(application.get("app_type") in ("EIA", "Pre-application") for application in not_consultation):
        if all(application.get("app_state") == "Withdrawn" for application in not_consultation):
            state = "Withdrawn"
            return state
        state = "Pre-application"
        return state

    for application in site_group:
        if application.get("app_type") == "Full":
            if application.get("app_state") in ("Permitted","Conditions"):
                state = "Permitted"
                return state

    if not any(application.get("app_type") in ("Full","Outline") for application in site_group):
        for application in site_group:
            if application.get("app_type") in ("Conditions", "Amendment"):
                if application.get("app_state") in ("Permitted", "Conditions"):
                    state = "Pre-approved"
                    return state

    for application in site_group:
        if application.get("app_type") in ("Full", "Outline", "Amendment","Conditions"):
            if application.get("app_state") in ("Undecided", "Unresolved","Referred"):
                state = "In progress"
                return state
        if application.get("app_type") == "Outline":
            if application.get("app_state") in ("Permitted", "Conditions"):
                state = "In progress"
                return state 
   
    remaining = [application for application in site_group if application.get("app_type") not in ("EIA", "Pre-application", "Consultation")]

    if remaining and all(application.get("app_state") in ("Rejected", "Withdrawn") for application in remaining):
        if any(application.get("app_state") == "Rejected" for application in remaining):
            state = "Rejected"
            return state
        state = "Withdrawn"
        return state

    state = "Unknown"
    return state

def find_first_submitted(site_group): # find earliest start_date

    first_submitted = min((application.get("start_date") for application in site_group if application.get("start_date")), default=None)
    return first_submitted

def find_first_permitted(site_group): # find earliest decided_date for full, and if not for conditions or amendment

    dates = [application.get("decided_date") for application in site_group if application.get("decided_date") and application.get("app_type") == "Full" and application.get("app_state") in ("Permitted", "Conditions")]
    if dates:
        return min(dates)

    if not any(application.get("app_type") in ("Full", "Outline") for application in site_group):
        other_dates = [application.get("decided_date") for application in site_group if application.get("decided_date") and application.get("app_type") in ("Conditions", "Amendment") and application.get("app_state") in ("Permitted", "Conditions")]
        return max(other_dates, default=None)

    return None

def find_latest_activity(site_group): #most recent of start_date or decided_date

    dates = []
    for application in site_group:
        if application.get("start_date"):
            start_date = application.get("start_date")
            dates.append(start_date)

        if application.get("decided_date"):
            decided_date = application.get("decided_date")
            dates.append(decided_date)

    latest_activity = max(dates, default=None)
    return latest_activity

def convert_number(number):

    if number:
        return float(number)
    return None

def build_json(sites): # defining shape of output json

    output_data = []

    for site_no, site_group in sites.items():
        
        output_fields  = {
            "site_no" : site_no,
            "name" : simple_pick(site_group, "name"),
            "description" : simple_pick(site_group, "description"),
            "link" : simple_pick(site_group, "link"),
            "applicants" : simple_aggregate(site_group, "applicant_company"),
            "agents" : simple_aggregate (site_group, "agent_company"),
            "references" : simple_aggregate(site_group, "uid"),
            "address" : location_pick(site_group, "address"),
            "postcode" : location_pick(site_group, "postcode"),
            "long" : convert_number(location_pick(site_group, "location_x")),
            "lat" : convert_number(location_pick(site_group, "location_y")),
            "state" : pick_state(site_group),
            "category" : simple_pick(site_group, "category"),
            "main_authority" : pick_main_authority(site_group),
            "authorities" : simple_aggregate(site_group, "area_name"),
            "first_submitted" : find_first_submitted(site_group),
            "first_permitted" : find_first_permitted(site_group),
            "latest_activity" : find_latest_activity(site_group),
            "power" : convert_number(simple_pick(site_group, "power_mw")),
            "size" : convert_number(simple_pick(site_group, "size_sqft")),
            "n_comments" : add_n_comments(site_group),
            "notes" : simple_aggregate(site_group, "notes"),
            "conflicts" : find_conflicts(site_group)
        }

        output_data.append(output_fields)

    return output_data

def main():

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    with open(input_filename + ".csv", encoding="utf-8-sig", newline="") as f:
        data = list(csv.DictReader(f))

    #remove false positives and communication infrastructure
    data = [row for row in data if row.get("category") not in ("false_positive","telco")]

    #organise data into site groups
    sites = {}
    for row in data:
        site_no = row["site_no"]
        if site_no not in sites:
            sites[site_no] = []
        sites[site_no].append(row)

    output_data = build_json(sites)

    #export as both json and csv
    with open(output_filename + "csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_data[0].keys())
        writer.writeheader()
        for site in output_data:
            row = {key: "; ".join(value) if isinstance(value, list) else value for key, value in site.items()}
            writer.writerow(row)

    with open(output_filename + "json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent =2, ensure_ascii=False)

main()
