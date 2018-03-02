#!./.venv/bin/python

"""Usage:
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
"""
from docopt import docopt

import suds
import suds.client
import configparser
import csv
import json
import urllib.request
import logging
import os


CONF = configparser.ConfigParser()
CONF.read('viimu.props')
url = CONF.get('Auth Header', 'url')
loglevel = CONF.get('Logging', 'LogLevel')


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filename=CONF.get('Logging', 'FileName'),
                    filemode='w')

if loglevel == 'DEBUG':
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class Service(object):
    def __init__(self, url=url):
        self.client = suds.client.Client(url)
        header = self.client.factory.create('AuthHeader')
        header.Domain = CONF.get('Auth Header', 'domain')
        header.UserId = CONF.get('Auth Header', 'userid')
        header.UserPassword = CONF.get('Auth Header', 'userpassword')
        header.OemId = CONF.get('Auth Header', 'oemid')
        header.OemPassword = CONF.get('Auth Header', 'oempassword')
        self.client.set_options(soapheaders=header)
        self.orgid = self.client.service.OrganizationQueryRoot()[0]
        self.orgidarray = self.client.factory.create('ArrayOfstring')
        self.orgidarray.string.append(self.orgid)


class Member(object):
    def __init__(self, service):
        self.member = service.client.factory.create('Member')
        self.cmemail = service.client.factory.create('ContactMethodEmail')


class MemberRequest(object):
    def __init__(self, service, args):
        self.service = service
        self.filename = args.get('-f', None)
        self.args = args
        self.action = args.get('-a', None)
        self.subaction = args.get('<subaction>', None)
        self.sync = args.get('-s', 'FALSE')

        if self.action in ('QUERY', 'ADD', 'UPDATE', 'DELETE'):
            if self.action == 'QUERY':
                if self.subaction in ('MEMBERS', 'CMS', 'CFS'):
                    self.query()
                else:
                    print('Invalid option. %s' % self.subaction)
                    exit(__doc__)

            if self.action == 'ADD':
                if self.filename is None:
                    print('Must pass in a file when using ADD. eg. ./viimu.py -f members.csv -a ADD')
                    exit(__doc__)
                else:
                    self.add_update('ADD')

            if self.action == 'UPDATE':
                if self.filename is None:
                    print('Must pass in a file when using ADD. eg. ./viimu.py -f members.csv -a ADD')
                    exit(__doc__)
                else:
                    self.add_update('UPDATE')

            if self.action == 'DELETE':
                if self.filename is None:
                    print('Must pass in a file when using DELETE. eg. ./viimu.py -f members.csv -a DELETE')
                    exit(__doc__)
                else:
                    try:
                        os.remove('members.json')
                    except OSError:
                        pass
                    self.delete()
        else:
            print('%s not a valid action.(QUERY, ADD, UPDATE, DELETE)' % self.action)
            exit(__doc__)

    def query(self):
        if self.subaction == 'MEMBERS':
        # Writes out a JSON file of member login names and Id's to be deleted.
            if self.filename is None:
                print('''Must pass in a file to query members.
                        eg. ./viimu.py -f members.csv -a QUERY MEMBERS''')
                exit(__doc__)
            else:
                reader = csv.DictReader(open(self.filename, 'rU'))
                usernames = [row['Username'] for row in reader]
                memberlist = []
                try:
                    for name in chunker(usernames, 299):
                        userdict = {}
                        # print(name)
                        strmembers = self.service.client.factory.create('ArrayOfstring')
                        strmembers.string.append(name)
                        members = self.service.client.service.MemberQueryByUsername(strmembers)
                        try:
                            if len(members.Member) == 0:
                                pass
                            else:
                                for member in members:
                                    strmember, listofmembers = member
                                    for i, m in enumerate(listofmembers):
                                        userdict[listofmembers[i].Username] = listofmembers[i].MemberId
                                memberlist.append(userdict)
                        except AttributeError as e:
                            logging.exception('An error has occurred. %s' % e)
                            pass
                    if len(memberlist) > 0:
                        try:
                            with open('members.json', 'w') as f:
                                f.write(json.dumps(memberlist, indent=4))
                            print('members.json has been successfully written out with active members found.')
                        except IOError as e:
                            print(e)
                except suds.WebFault as e:
                    logging.exception(
                        'An error has occurred. %s' % e.fault.detail)
                    print(e.fault.detail)

        if self.subaction == 'CMS':  # Contact Methods
            cms = self.service.client.service.AvailableContactMethodQueryByOrganizationId(
                self.service.orgid)
            for cm in cms:
                strcm, cm = cm
                for c in cm:
                    print('%s_%s_%s (%s)' % (c.Transport,
                                             c.Qualifier,
                                             c.Ordinal,
                                             c.DisplayName))

        if self.subaction == 'CFS':  # Custom Fields
            cfs = self.service.client.service.OrganizationCustomFieldQueryByOrganizationId(
                self.service.orgidarray, 0, 300)
            for cf in cfs:
                strcf, cf = cf
                for c in cf:
                    print('CF_%s' % (c.Name))


    def add_update(self, action):
            membermodel = Member(self.service)

            reader = csv.DictReader(open('LA04.csv', 'rU'))
            usernames = [row['Username'] for row in reader]

            # Store names of Member Object attributes in a list.
            memberfields = []
            cmfields = []
            cffields = []
            cfdict = {}
            for attributes in membermodel.member:
                k, v = attributes
                memberfields.append(k)

            contactmethods = self.service.client.service.AvailableContactMethodQueryByOrganizationId(self.service.orgid)
            customfields = self.service.client.service.OrganizationCustomFieldQueryByOrganizationId(self.service.orgidarray, 0, 300)

            for cm in contactmethods:
                strcm, cm = cm
                for c in cm:
                    cmfields.append(str('%s_%s_%s' % (c.Transport, c.Qualifier, c.Ordinal)))

            for cf in customfields:
                strcf, cf = cf
                for c in cf:
                    cffields.append('CF_%s' % (c.Name))
                    cfdict['CF_' + str(c.Name)] = c.OrganizationCustomFieldId

            # Create new reader to iterate.
            reader = csv.DictReader(open(self.filename, 'rU'))

            rows = []
            for row in reader:
                rows.append(row)

            # Read Usernames in from source file.
            for name in chunker(usernames, 299):
                # Create Dict to store Username:MemberId
                userdict = {}
                # Create a string array to hold Usernames
                strmembers = self.service.client.factory.create('ArrayOfstring')
                strmembers.string.append(name)
                memberids = self.service.client.service.MemberQueryByUsername(strmembers)

                for member in memberids:
                    strmember, listofmembers = member

                for i, m in enumerate(listofmembers):
                    userdict[listofmembers[i].Username] = listofmembers[i].MemberId

                for row in chunker(rows, 299):
                    # Create Member Array
                    members = self.service.client.factory.create('ArrayOfMember')
                    for x in row:
                        # Create Member Object
                        m = Member(self.service)
                        cms = self.service.client.factory.create('ArrayOfContactMethod')
                        cfs = self.service.client.factory.create('ArrayOfMemberCustomField')
                        # Iterate through row data and assign member attributes if they exist in file.
                        for k, v in x.items():
                            if k in cmfields:
                                if not v:
                                    pass
                                else:
                                    if k.split('_')[0] == 'Email':
                                        cm = self.service.client.factory.create('ContactMethod')
                                        cmemail = self.service.client.factory.create('ContactMethodEmail')
                                        cmemail.Qualifier = k.split('_')[1]
                                        cmemail.Ordinal = k.split('_')[2]
                                        cmemail.EmailAddress = v
                                        cm.ContactMethodEmail = cmemail
                                        cms.ContactMethod.append(cm)

                                    if k.split('_')[0] == 'Phone':
                                        cm = self.service.client.factory.create('ContactMethod')
                                        cmphone = self.service.client.factory.create('ContactMethodPhone')
                                        cmphone.Qualifier = k.split('_')[1]
                                        cmphone.Ordinal = k.split('_')[2]
                                        cmphone.PhoneNum = v
                                        cm.ContactMethodPhone = cmphone
                                        cms.ContactMethod.append(cm)

                                    if k.split('_')[0] == 'Sms':
                                        cm = self.service.client.factory.create('ContactMethod')
                                        cmsms = self.service.client.factory.create('ContactMethodSMS')
                                        cmsms.Qualifier = k.split('_')[1]
                                        cmsms.Ordinal = k.split('_')[2]
                                        cmsms.PhoneNum = v
                                        cm.ContactMethodSMS = cmsms
                                        cms.ContactMethod.append(cm)

                                    if k.split('_')[0] == 'Fax':
                                        cm = self.service.client.factory.create('ContactMethod')
                                        cmfax = self.service.client.factory.create('ContactMethodFax')
                                        cmfax.Qualifier = k.split('_')[1]
                                        cmfax.Ordinal = k.split('_')[2]
                                        cmfax.PhoneNum = v
                                        cm.ContactMethodFax = cmfax
                                        cms.ContactMethod.append(cm)
                            if k in cffields:
                                cf = self.service.client.factory.create('MemberCustomField')
                                cf.Value = v
                                cf.OrganizationCustomFieldId = cfdict[k]
                                cfs.MemberCustomField.append(cf)
                            if k in memberfields:
                                m.member[k] = v
                                m.member.ContactMethods = cms
                                m.member.MemberCustomFields = cfs
                        if action == 'ADD':
                            members.Member.append(m.member)
                        if action == 'UPDATE':
                            if m.member.Username in userdict:
                                # Set MemberId from Dictionary values
                                m.member.MemberId = userdict[m.member.Username]
                                if m.member.MemberId is not None:
                                    # Append Member Object to Member Array
                                    members.Member.append(m.member)
                    try:
                        logging.info(members)
                        if action == 'ADD':
                            logging.info(members)
                            # results = self.service.client.service.MemberCreate(members)
                        if action == 'UPDATE':
                            logging.info(members)
                            # logging.info(self.service.client.service.MemberUpdate(members, '%s' % self.sync))
                    except suds.WebFault as e:
                        logging.exception('An error has occurred. %s' % e.fault.detail)
                        print(e.fault.detail)

    def delete(self):
        try:
            memberids = json.load(open(self.filename, 'r'))
            numMembers = 0
            for num in memberids:
                numMembers += len(num)

            confirmation = raw_input('Are you sure you want to delete %d users? yes/no: ' % numMembers)

            if confirmation == 'yes':
                print('Processing Deletes...')

                for memberdict in memberids:
                    try:
                        memberstring = self.service.client.factory.create(
                            'ArrayOfstring')
                        for k, v in memberdict.items():
                            memberstring.string.append(v)

                        deletes = self.service.client.service.MemberDeleteById(
                            memberstring)
                        print(deletes)
                        logging.info(deletes)
                    except Exception as e:
                        logging.exception('An error has occurred. %s' % e)
                        print(e)
            else:
                print('Halting execution.  Exiting.')

        except ValueError as e:
            logging.exception('An error has occurred. %s' % e)
            print('Exiting. Not a valid JSON file.')


def main():
    args = docopt(__doc__, version='0.1')

    try:
        service = Service()
        MemberRequest(service, args)
    except (suds.WebFault, urllib.request.URLError, configparser.NoOptionError, AttributeError) as e:
        logging.exception('An error has occurred. %s' % e)
        print('An error has occurred. %s' % e)

if __name__ == '__main__':
    main()

