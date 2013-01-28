# ViiMU - Varolii Member Utility

## About

This utility was created to allow you to ADD, UPDATE, DELETE members using data in csv format.

##Installation
Note - ViiMU requires suds.  [SUDS](https://fedorahosted.org/suds/)

    pip install suds
    git clone https://github.com/tpe11etier/viimu.git

##Usage

    Usage:
    viimu.py [-f filename] [-a <action> <subaction>] [-s <sync>]
    viimu.py -h | --help | -v | --version

    Options:
    -h --help                 show this help message and exit
    -v --version               show version and exit
    -f <filename>             filename to parse.
                            Note - filename is not required when querying contact methods(CMS)
                              and custom fields(CFS).
    -a <action> <subaction>   actions to perform.  [QUERY, ADD, UPDATE, DELETE] [MEMBERS, CFS, CMS]
    -s <sync>                 when using UPDATE, set to TRUE or FALSE. Note - defaults value is FALSE
                            False if the given members augment information in the Varolii Profiles database.
                            True if the given members replace the existing subscriptions in the Varolii Profiles database.

##Example Usage and Details
ViiMU will use the csv header row to create the [Member object](https://ws.envoyprofiles.com/WebService/EPAPI_1.0/object/Member.htm).
For that reason, the header needs to match **exactly**.  For example.  To create a Member, **Username** and **Password** are required attributes.
The csv column headers must be **Username** and **Password**.  **USERName** or **PASSWORD** will not work.

---

###QUERY
QUERY is used to query members(MEMBERS), organization contact methods(CMS) and organization custom fields(CFS).

Contact methods can be queried and the return values will be used as the column header.

Note - Only Phone, Email, SMS and Fax are supported at this time.

    [tonypelletier@tpelletiermac:viimu]$ ./viimu.py -a QUERY CMS
    Phone_Office_0 (Work Phone)
    Phone_Home_0 (Home Phone)
    Phone_Cell_0 (Cell Phone)
    Sms_None_0 (SMS)
    Email_Office_0 (Work Email)
    Email_Home_0 (Home Email)
    AlphaPager_None_0 (Alpha Pager)
    AlphaPager_None_0 (Alpha Pager Carrier)
    Fax_Office_0 (Fax)

Custom fields can be queried and the return values will be used as the column header.

Note - In order to determine what column headers are custom fields, I am using **CF_** as a prefix.
Your Custom field headers should also include the **CF_**.

    [tonypelletier@tpelletiermac:viimu]$ ./viimu.py -a QUERY CFS
    CF_Seniority#
    CF_STATUS
    CF_Building
    CF_Floor
    CF_boolean

The member query is used to pass in a csv of members that you would like to delete.  I made deleting members a two step process to avoid
accidental deletion.

Query members from a csv which writes out a json file that contains member Username's and MemberId's.

    [tonypelletier@tpelletiermac:viimu]$ ./viimu.py -f members.csv -a QUERY MEMBERS
    ['BMarchand', 'TRask']
    members.json has been successfully written out with active members found.
    [tonypelletier@tpelletiermac:viimu]$ less members.json
    [
        {
            "TRask": "kmhyhkj67",
            "BMarchand": "kmhdtkj67"
        }
    ]
    members.json (END)

---

###DELETE

Delete the members using the json file.

    [tonypelletier@tpelletiermac:viimu]$ ./viimu.py -f members.json -a DELETE
    (ArrayOfstring){
       string[] =
          "kmhyhkj67",
          "kmhdtkj67",
     }
    Are you sure you want to delete 2 users? yes/no: yes
    Processing Deletes...
    (ArrayOfboolean){
       boolean[] =
          True,
          True,
     }

---

###ADD

Add members using csv file passed in.

    [tonypelletier@tpelletiermac:viimu]$ ./viimu.py -f members.csv -a ADD
    (ArrayOfResponseEntry){
       ResponseEntry[] =
          (ResponseEntry){
             Id = "k85jhkj67"
             Warnings = ""
          },
          (ResponseEntry){
             Id = "k85itkj67"
             Warnings = ""
          },
     }

---

###UPDATE

Update members using csv file passed in.  When updating members, you can also use the -s option with a value of TRUE or FALSE(Default).
FALSE if the given members augment information in the Varolii Profiles database.
TRUE if the given members replace the existing subscriptions in the Varolii Profiles database.

    [tonypelletier@tpelletiermac:viimu]$ ./viimu.py -f members.csv -a UPDATE -s FALSE
    ['BMarchand', 'TRask']
    (ArrayOfResponseEntry){
       ResponseEntry[] =
          (ResponseEntry){
             Id = "k85jhkj67"
             Warnings = ""
          },
          (ResponseEntry){
             Id = "k85itkj67"
             Warnings = ""
          },
     }

