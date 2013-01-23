#!/usr/bin/env python

import sys
import suds
import ConfigParser
import csv
import json
import argparse


CONF = ConfigParser.ConfigParser()
CONF.read("viimu.props")
url = CONF.get("Auth Header", "url")


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


class Service(object):

    def __init__(self, url=url):
        self.client = suds.client.Client(url)
        header = self.client.factory.create('AuthHeader')
        header.Domain = CONF.get("Auth Header", "domain")
        header.UserId = CONF.get("Auth Header", "userid")
        header.UserPassword = CONF.get("Auth Header", "userpassword")
        header.OemId = CONF.get("Auth Header", "oemid")
        header.OemPassword = CONF.get("Auth Header", "oempassword")
        self.client.set_options(soapheaders=header)
        self.orgid = self.client.service.OrganizationQueryRoot()[0]
        self.orgidarray = self.client.factory.create('ArrayOfstring')
        self.orgidarray.string.append(self.orgid)


class Member(object):
    def __init__(self, service):
        self.member = service.client.factory.create('Member')
        self.cmemail = service.client.factory.create('ContactMethodEmail')


class MemberRequest(object):
    def __init__(self, service, filename=None, action=None):
        self.service = service
        self.action = action
        self.filename = filename

        if self.action[0] in ('QUERY', 'ADD', 'UPDATE', 'DELETE'):

            if self.action[0] == 'QUERY':
                if len(self.action) > 1:
                    if self.action[1] and self.action[1] in ('MEMBERS',
                                                             'CMS',
                                                             'CFS'):
                        if self.action[1] == 'MEMBERS':
                        # Writes out a JSON file of member login names and Id's to be deleted.
                            if self.filename is None:
                                print 'Must pass in a file to query members.  \
                                eg. -f members -a QUERY MEMBERS'
                            else:
                                self.reader = csv.DictReader(
                                    open(self.filename, 'rU'))
                                self.usernames = [
                                    row['Username'] for row in self.reader]
                                self.query()
                        if self.action[1] == 'CMS':  # Contact Methods
                            cms = self.service.client.service.AvailableContactMethodQueryByOrganizationId(
                                self.service.orgid)
                            for cm in cms:
                                strcm, cm = cm
                                for c in cm:
                                    print '%s_%s_%s (%s)' % (c.Transport,
                                                             c.Qualifier,
                                                             c.Ordinal,
                                                             c.DisplayName)

                        if self.action[1] == 'CFS':  # Custom Fields
                            cfs = self.service.client.service.OrganizationCustomFieldQueryByOrganizationId(
                                self.service.orgidarray, 0, 300)
                            print cfs
                    else:
                        print '''Invalid option passed into QUERY action. (MEMBERS, CMS, CFS)
                                 eg. -a QUERY MEMBERS'''

            if self.action[0] == 'ADD':

                # membermodel = Member(self.service)
                self.reader = csv.DictReader(open(self.filename, 'rU'))
                self.header = self.reader.fieldnames
                self.add()

            if self.action[0] == 'DELETE':
                try:
                    self.memberids = json.load(open(self.filename, 'r'))
                    self.delete()
                except ValueError:
                    print 'Exiting. Not a valid JSON file.'
        else:
            print '%s not a valid action.(QUERY, ADD, UPDATE, DELETE)' % self.action
            sys.exit()

    def query(self):
        #TODO - Doc
        userlist = []
        try:
            for name in chunker(self.usernames, 299):
                userdict = {}
                print name
                strmembers = self.service.client.factory.create(
                    'ArrayOfstring')
                strmembers.string.append(name)
                members = self.service.client.service.MemberQueryByUsername(
                    strmembers)

                try:
                    if len(members) == 0:
                        print 'No Members found.'
                    else:
                        for member in members:
                            strmember, listofmembers = member

                            for i, m in enumerate(listofmembers):
                                userdict[listofmembers[
                                    i].Username] = listofmembers[i].MemberId

                        userlist.append(userdict)
                except AttributeError as e:
                    print 'No Members found.'

            try:
                with open('members.json', 'wa') as f:
                    f.write(json.dumps(userlist, indent=4))

                print 'members.json has been successfully written out.'
            except IOError as e:
                print e
        except suds.WebFault as e:
            print e.fault.detail

    def add(self):
        members = self.service.client.factory.create('ArrayOfMember')
        membermodel = Member(self.service)

        memberfields = []
        cmfields = []

        for attributes in membermodel.member:
            k, v = attributes
            memberfields.append(k)

        cms = self.service.client.service.AvailableContactMethodQueryByOrganizationId(
            self.service.orgid)

        for cm in cms:
            strcm, cm = cm
            for c in cm:
                cmfields.append(
                    str('%s_%s_%s' % (c.Transport, c.Qualifier, c.Ordinal)))

        for row in self.reader:
            m = Member(self.service)
            cms = self.service.client.factory.create('ArrayOfContactMethod')
            for k, v in row.items():
                if k in cmfields:
                    if k.split('_')[0] == 'Email':
                        cm = self.service.client.factory.create(
                            'ContactMethod')
                        cmemail = self.service.client.factory.create(
                            'ContactMethodEmail')
                        cmemail.Qualifier = k.split('_')[1]
                        cmemail.Ordinal = k.split('_')[2]
                        cmemail.EmailAddress = v
                        cm.ContactMethodEmail = cmemail
                        cms.ContactMethod.append(cm)

                    if k.split('_')[0] == 'Phone':
                        cm = self.service.client.factory.create(
                            'ContactMethod')
                        cmphone = self.service.client.factory.create(
                            'ContactMethodPhone')
                        cmphone.Qualifier = k.split('_')[1]
                        cmphone.Ordinal = k.split('_')[2]
                        cmphone.PhoneNum = v
                        cm.ContactMethodPhone = cmphone
                        cms.ContactMethod.append(cm)

                    if k.split('_')[0] == 'Sms':
                        cm = self.service.client.factory.create(
                            'ContactMethod')
                        cmsms = self.service.client.factory.create(
                            'ContactMethodSMS')
                        cmsms.Qualifier = k.split('_')[1]
                        cmsms.Ordinal = k.split('_')[2]
                        cmsms.PhoneNum = v
                        cm.ContactMethodSMS = cmsms
                        cms.ContactMethod.append(cm)

                    if k.split('_')[0] == 'Fax':
                        cm = self.service.client.factory.create(
                            'ContactMethod')
                        cmfax = self.service.client.factory.create(
                            'ContactMethodFax')
                        cmfax.Qualifier = k.split('_')[1]
                        cmfax.Ordinal = k.split('_')[2]
                        cmfax.PhoneNum = v
                        cm.ContactMethodFax = cmfax
                        cms.ContactMethod.append(cm)

                if k in memberfields:
                    m.member[k] = v
                    m.member.ContactMethods = cms

            members.Member.append(m.member)

        try:
            print self.service.client.service.MemberCreate(members)
        except suds.WebFault as e:
            print e.fault.detail

    def update(self):
        pass

    def delete(self):
        for k, v in self.memberids.items():
            self.stringmembers.string.append(v)
        print self.stringmembers

        try:
            confirmation = raw_input('Are you sure you want to delete %d users? yes/no: ' % len(
                self.stringmembers.string))
            if confirmation == 'yes':
                print "Processing Deletes..."
                try:
                    print self.service.client.service.MemberDeleteById(
                        self.stringmembers)
                except suds.WebFault as e:
                    print e.fault.detail
            else:
                print 'Halting execution.  Exiting.'
                sys.exit()
        except Exception as e:
            print e


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Specify the file.', default=None)
    parser.add_argument('-a',
                        '--action',
                        nargs='+',
                        help='Specify the action. (QUERY, ADD, UPDATE, DELETE)', default=None)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.1', default=None)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    service = Service()
    MemberRequest(service, args.file, args.action)


if __name__ == '__main__':
    main()
