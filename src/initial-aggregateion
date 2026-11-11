"""Script to sort applications into groups which likely describe the same site
or development before manual verification.

It groups applications in two ways:

1) Finding applications which mention the reference number of another application
in their description.
2) Finding applications which share both postcode and text address description.

It then assigns each group of applications a site number."""

import sys
import json

def matching_list(match_list, match): #add matches to match list

    for reference in match_list:
        if reference & match:
            reference.update(match)
            break    

    else:
        match_list.append(match) 

    return match_list

def common_reference(data, match_list): #identify refrences in description

    references = {row["uid"] for row in data if row.get("uid")}

    for row in data:
        
        if not row.get("uid"):
            continue

        own_reference = row["uid"]
        description = row.get("description") or ""

        for reference in references:        
            if reference in description and reference != own_reference:
                match = {own_reference, reference}
                matching_list(match_list, match)

    return match_list

def postcode_address_match(data, match_list): #identfy strongly matching locations

    for row in data:

        if not row.get("postcode") or not row.get ("address") or not row.get("uid"):
            continue

        else:
            own_reference = row["uid"]
            own_postcode = row["postcode"]
            own_address = row["address"]
            
            for other_row in data:

                reference = other_row.get("uid")

                if reference == own_reference:
                    continue

                if other_row.get("postcode") == own_postcode and other_row.get("address") == own_address:
                    match = {own_reference, reference}
                    matching_list(match_list, match) 

    return match_list

def merge_sets(match_list): #merge any sets with overlaps
     
    merged_data = [set(match) for match in match_list]
    changes_made = True

    while changes_made is True:
        changes_made = False
        row_n = 0

        while row_n < len(merged_data):

            for other_row_n in range(row_n + 1, len(merged_data)):

                if merged_data[other_row_n] & merged_data[row_n]:
                    merged_data[row_n].update(merged_data[other_row_n])

                    del merged_data[other_row_n]
                    changes_made = True
                    break
                
            row_n = row_n + 1

    merged_data.sort(key=len, reverse=True)
    return merged_data

def compile_json(merged_data, data): #compilling new JSON with site numbers

    for site_no, match in enumerate(merged_data, start=1):

        for row in data:
            reference = row.get("uid")
            if reference in match:
                row["site_no"] = f"SITE{site_no:04d}"


    site_no = len(merged_data)
    for row in data:
        if not row.get("site_no"):
            site_no = site_no + 1
            row["site_no"] = f"SITE{site_no:04d}"

    data.sort(key=lambda row:row["site_no"])
    return data

def main(): #export json

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    match_list = []

    common_reference(data, match_list)
    postcode_address_match(data, match_list)
    
    merged_data = merge_sets(match_list)
    data = compile_json(merged_data, data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent =2)

main()
