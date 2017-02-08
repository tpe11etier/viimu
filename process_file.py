#!/usr/bin/env python3

# Imports
import csv
import time

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
    "HOME_TEL__C": "Phone_Home_0",
    "WORK_EMAIL__C": "Email_Office_0",
    "WORK_MOBILE__C": "Phone_Cell_0",
    "WORK_SMS__C": "Sms_None_0",
    "WORK_TEL__C": "Phone_Office_0"
}

customer_dict = {
    "EMPLOYEE_ID__C": "Username",
    "EMPLOYEE_ID__C": "Recipient PIN",
    "FF__FIRST_NAME__C": "FirstName",
    "FF__LAST_NAME__C": "LastName",
    "COST_CENTER__C" : "CF_7 Cost Center",
    "EMPLOYEE_HOME_CITY__C" : "CF_Home City",
    "EMPLOYEE_HOME_STATE_PROVINCE__C" : "CF_Home State/Province",
    "EMPLOYEE_HOME_ZIP_POSTAL_CODE__C" : "CF_Home Zip/Postal Code",
    "EMPLOYEE_ID_C": "CF_2 Emp ID",
    "EMPLOYEE_STATUS__C": "CF_x Employee Status",
    "FF__TITLE__C": "CF_6 Title",
    "HR_BUSINESS_UNIT__C": "CF_4 Business Unit",
    "HR_DIVISION__C": "CF_3 Division",
    "INACTIVE_STATUS__C": "CF_y Inactive Status",
    "MAIL_DROP__C": "CF_Work Mail Drop",
    "MANAGER_NAME__C": "CF_Manager Name",
    "MANAGERS_ID__C": "CF_Manager ID",
    "PREFERRED_FIRST_NAME__C": "CF_1 Preferred First Name",
    "SITE_CITY__C": "CF_Work City",
    "SITE_STATE_PROVINCE__C": "CF_Work State/Province",
    "SUB_BUSINESS_UNIT__C": "CF_5 Department",
    "WORK_STREET_ADDRESS__C": "CF_Work Location",
    "HOME_TEL__C": "Phone_Home_0",
    "WORK_EMAIL__C": "Email_Office_0",
    "WORK_MOBILE__C": "Phone_Cell_0",
    "WORK_SMS__C": "Sms_None_0",
    "WORK_TEL__C": "Phone_Office_0"
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
    dict_headers['CF_2 Emp ID'] = 'CF_2 Emp ID'
    dict_headers['AccountEnabled'] = 'AccountEnabled'
    dict_headers['Password'] = 'Password'
    writer = csv.DictWriter(open('extract_out_%s.csv' % time.strftime("%Y%m%d"),  "w",encoding='utf-8', errors='ignore'), dict_headers,extrasaction='ignore')
    print(dict_headers)
    writer.writeheader()
    for line in reader:
        writer.writerow({dict_headers['Username']: line['EMPLOYEE_ID__C'],
                         dict_headers['Recipient PIN']: line['EMPLOYEE_ID__C'],
                         dict_headers['CF_2 Emp ID']: line['EMPLOYEE_ID__C'],
                         dict_headers['FirstName']: line['FF__FIRST_NAME__C'],
                         dict_headers['LastName']: line['FF__LAST_NAME__C'],
                         dict_headers['CF_7 Cost Center']: line['COST_CENTER__C'],
                         dict_headers['CF_Home City']: line['EMPLOYEE_HOME_CITY__C'],
                         dict_headers['CF_Home State/Province']: line['EMPLOYEE_HOME_STATE_PROVINCE__C'],
                         dict_headers['CF_Home Zip/Postal Code']: line['EMPLOYEE_HOME_ZIP_POSTAL_CODE__C'],
                         dict_headers['CF_x Employee Status']: line['EMPLOYEE_STATUS__C'],
                         dict_headers['CF_6 Title']: line['FF__TITLE__C'],
                         dict_headers['CF_4 Business Unit']: line['HR_BUSINESS_UNIT__C'],
                         dict_headers['CF_3 Division']: line['HR_DIVISION__C'],
                         dict_headers['CF_y Inactive Status']: line['INACTIVE_STATUS__C'],
                         dict_headers['CF_Work Mail Drop']: line['MAIL_DROP__C'],
                         dict_headers['CF_Manager Name']: line['MANAGER_NAME__C'],
                         dict_headers['CF_Manager ID']: line['MANAGERS_ID__C'],
                         dict_headers['CF_1 Preferred First Name']: line['PREFERRED_FIRST_NAME__C'],
                         dict_headers['CF_Work City']: line['SITE_CITY__C'],
                         dict_headers['CF_Work State/Province']: line['SITE_STATE_PROVINCE__C'],
                         dict_headers['CF_5 Department']: line['SUB_BUSINESS_UNIT__C'],
                         dict_headers['CF_Work Location']: line['WORK_STREET_ADDRESS__C'],
                         dict_headers['Phone_Home_0']: line['HOME_TEL__C'],
                         dict_headers['Email_Office_0']: line['WORK_EMAIL__C'],
                         dict_headers['Phone_Cell_0']: line['WORK_MOBILE__C'],
                         dict_headers['Sms_None_0']: line['WORK_SMS__C'],
                         dict_headers['Phone_Office_0']: line['WORK_TEL__C'],
                         dict_headers['AccountEnabled']: 'True',
                         dict_headers['Password']: 'JohnHancock$1',
                         })




if __name__ == '__main__':
    # Test Comment
    process_file('extract_small.csv')
