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

customer_dict = {
    "EMPLOYEE_ID__C": "Username",
    "EMPLOYEE_ID__C": "Recipient PIN",
    "FF__FIRST_NAME__C": "First Name",
    "FF__LAST_NAME__C": "Last Name",
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
    "WORK_STREET_ADDRESS__C": "Work Location",
    "HOME_TEL__C": "Home Phone",
    "WORK_EMAIL__C": "Work Email",
    "WORK_MOBILE__C": "Cell Phone",
    "WORK_SMS__C": "SMS",
    "WORK_TEL__C": "Work Phone"
}
converted_headers = {}


def process_file(filename):
    reader = csv.DictReader(open(filename,  "r",encoding='utf-8', errors='ignore'))
    headers = reader.fieldnames
    for header in headers:
        if header in dict_contact_info or header in dict_custom_fields or header in dict_contact_devices:
            converted_headers[header] = customer_dict[header]
    dict_headers = dict((v, v) for k,v in converted_headers.items())
    dict_headers['Username'] = 'Username'
    dict_headers['Recipient PIN'] = 'Recipient PIN'
    dict_headers['2 Emp ID'] = '2 Emp ID'
    writer = csv.DictWriter(open('extract_out.csv',  "w",encoding='utf-8', errors='ignore'), dict_headers,extrasaction='ignore')
    print(dict_headers)
    writer.writeheader()
    for line in reader:
        writer.writerow({dict_headers['Username']: line['EMPLOYEE_ID__C'],
                         dict_headers['Recipient PIN']: line['EMPLOYEE_ID__C'],
                         dict_headers['2 Emp ID']: line['EMPLOYEE_ID__C'],
                         dict_headers['First Name']: line['FF__FIRST_NAME__C'],
                         dict_headers['Last Name']: line['FF__LAST_NAME__C'],
                         dict_headers['First Name']: line['FF__FIRST_NAME__C'],
                         dict_headers['7 Cost Center']: line['COST_CENTER__C'],
                         dict_headers['Home City']: line['EMPLOYEE_HOME_CITY__C'],
                         dict_headers['Home State/Province']: line['EMPLOYEE_HOME_STATE_PROVINCE__C'],
                         dict_headers['Home Zip/Postal Code']: line['EMPLOYEE_HOME_ZIP_POSTAL_CODE__C'],
                         dict_headers['x Employee Status']: line['EMPLOYEE_STATUS__C'],
                         dict_headers['6 Title']: line['FF__TITLE__C'],
                         dict_headers['4 Business Unit']: line['HR_BUSINESS_UNIT__C'],
                         dict_headers['3 Division']: line['HR_DIVISION__C'],
                         dict_headers['y Inactive Status']: line['INACTIVE_STATUS__C'],
                         dict_headers['Work Mail Drop']: line['MAIL_DROP__C'],
                         dict_headers['Manager Name']: line['MANAGER_NAME__C'],
                         dict_headers['Manager ID']: line['MANAGERS_ID__C'],
                         dict_headers['1 Preferred First Name']: line['PREFERRED_FIRST_NAME__C'],
                         dict_headers['Work City']: line['SITE_CITY__C'],
                         dict_headers['Work State/Province']: line['SITE_STATE_PROVINCE__C'],
                         dict_headers['5 Department']: line['SUB_BUSINESS_UNIT__C'],
                         dict_headers['Work Location']: line['WORK_STREET_ADDRESS__C'],
                         dict_headers['Home Phone']: line['HOME_TEL__C'],
                         dict_headers['Work Email']: line['WORK_EMAIL__C'],
                         dict_headers['Cell Phone']: line['WORK_MOBILE__C'],
                         dict_headers['SMS']: line['WORK_SMS__C'],
                         dict_headers['Work Phone']: line['WORK_TEL__C']})




if __name__ == '__main__':
    process_file('extract.csv')
