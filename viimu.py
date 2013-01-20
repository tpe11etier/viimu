#!/usr/bin/env python

import sys
import suds
import ConfigParser
import csv
import json
import argparse


CONF = ConfigParser.ConfigParser()
CONF.read("soap.props")
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


class Member(object):
    def __init__(self, service):
        self.member = service.client.factory.create('Member')
        self.cmemail = service.client.factory.create('ContactMethodEmail')




class MemberRequest(object):
    def __init__(self, service, filename, action):
        self.service = service
        self.action = action
        self.filename = filename

        if self.action in ('QUERY', 'ADD', 'UPDATE', 'DELETE'):
            if self.action == 'QUERY':
                self.reader = csv.DictReader(open(self.filename, 'rU'))
                self.usernames = [row['Username'] for row in self.reader]
                self.query()

            if self.action == 'ADD':
                membermodel = Member(self.service)
                self.reader = csv.DictReader(open(self.filename, 'rU'))
                self.header = self.reader.fieldnames
                self.add()

            if self.action == 'DELETE':
                try:
                    self.memberids = json.load(open(self.filename, 'r'))
                    self.delete()
                except ValueError as e:
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
                strmembers = self.service.client.factory.create('ArrayOfstring')
                strmembers.string.append(name)
                members = self.service.client.service.MemberQueryByUsername(strmembers)

                try:
                    for member in members:
                        strmember, listofmembers = member

                        for i, m in enumerate(listofmembers):
                            userdict[listofmembers[i].Username] = listofmembers[i].MemberId

                    userlist.append(userdict)
                except AttributeError as e:
                    print 'No Members found.'

            with open('members.json', 'a') as f:
                f.write(json.dumps(userlist, indent = 4))

            print 'members.json has been successfully written out.'
        except suds.WebFault as e:
            print e.fault.detail

    def add(self):
        members = self.service.client.factory.create('ArrayOfMember')
        membermodel = Member(self.service)

        memberfields = []
        cmemailfields = []

        for attributes in membermodel.member:
            k, v = attributes
            memberfields.append(k)

        for attributes in membermodel.cmemail:
            k, v = attributes
            cmemailfields.append(k)
        print cmemailfields

        for row in self.reader:
            m = Member(self.service)
            for k, v in row.items():
                if k in memberfields:
                    m.member[k] = v

            members.Member.append(m.member)


    def append(self):
        pass

    def update(self):
        pass

    def delete(self):
        for k, v in self.memberids.items():
            self.stringmembers.string.append(v)
        print self.stringmembers

        try:
            confirmation = raw_input('Are you sure you want to delete %d users? yes/no: ' % len(self.stringmembers.string))
            if confirmation == 'yes':
                print "Processing Deletes..."
                try:
                    print self.service.client.service.MemberDeleteById(self.stringmembers)
                except suds.WebFault as e:
                    print e.fault.detail
            else:
                print 'Halting execution.  Exiting.'
                sys.exit()
        except Exception as e:
            print e


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Specify the file.')
    parser.add_argument('-a', "--action", help='Specify the action. (QUERY, ADD, UPDATE, DELETE)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    service = Service()
    # m = MemberRequest(service, args.file, args.action)
    # m = MemberRequest(service, 'TPELLETIER_FULL.csv', 'QUERY')
    m = MemberRequest(service, 'members.csv', 'ADD')


if __name__ == '__main__':
    main()
