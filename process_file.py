#!/usr/bin/env python3

# Imports
import csv

# Dictionary containing mappings
dict_contact_info = {
    "EMPLOYEE_ID__C": "Username",
    "EMPLOYEE_ID__C": "Recipient PIN",
    "FF__FIRST_NAME__C": "First Name",
    "FF__LAST_NAME__C": "Last Name"
}

dict_custom_fields = {
    "COST_CENTER__C" : "7 Cost Center",
    "EMPLOYEE_HOME_CITY__C" : "Home City",
    "EMPLOYEE_HOME_STATE_PROVINCE__C" : "Home State/Province",
    "EMPLOYEE_HOME_ZIP_POSTAL_CODE__C" : "Home Zip/Postal Code",
    "EMPLOYEE_ID_C": "2 Emp ID",
    "EMPLOYEE_STATUS__C": "x Employee Status",
    "FF__TITLE__C": "6 Title",
    "HR_BUSINESS_UNIT__C": "4 Business Unit",
    "HR_DIVISION__C": "3 Division",
    "INACTIVE_STATUS__C": "y Inactive Status",
    "MAIL_DROP__C": "Work Mail Drop",
    "MANAGER_NAME__C": "Manager Name",
    "MANAGERS_ID__C": "Manager ID",
    "PREFERRED_FIRST_NAME__C": "1 Preferred First Name",
    "SITE_CITY__C": "Work City",
    "SITE_STATE_PROVINCE__C": "Work State/Province",
    "SUB_BUSINESS_UNIT__C": "5 Department",
    "WORK_STREET_ADDRESS__C": "Work Location"
}

dict_contact_devices = {
    "HOME_TEL__C": "Home Phone",
    "WORK_EMAIL__C": "Work Email",
    "WORK_MOBILE__C": "Cell Phone",
    "WORK_SMS__C": "SMS",
    "WORK_TEL__C": "Work Phone"
}

converted_headers = []

def process_file(filename):
    reader = csv.DictReader(open(filename,  "r",encoding='utf-8', errors='ignore'))
    headers = reader.fieldnames
    # print(headers)
    for header in headers:
        if header in dict_contact_info or header in dict_custom_fields or header in dict_contact_devices:
            converted_headers.append(header)
            # print(headers)
        else:
            pass
    print(converted_headers)

    with open('output.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=converted_headers)

        writer.writeheader()

    # for row in reader:
    #     print(row)
        # print(row['EMPLOYEE_ID__C'], row['FF__FIRST_NAME__C'])

if __name__ == '__main__':
    process_file('extract_small.csv')
