#!/usr/bin/env python

import sys
import suds
import ConfigParser
import csv
import json
import argparse
import urllib2


CONF = ConfigParser.ConfigParser()
CONF.read("viimu.props")
url = CONF.get("Auth Header", "url")


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


class Service(object):
    def __init__(self, url=url):
        try:
            self.client = suds.client.Client(url)
            try:
                header = self.client.factory.create('AuthHeader')
                header.Domain = CONF.get("Auth Header", "domain")
                header.UserId = CONF.get("Auth Header", "userid")
                header.UserPassword = CONF.get("Auth Header", "userpassword")
                header.OemId = CONF.get("Auth Header", "oemid")
                header.OemPassword = CONF.get("Auth Header", "oempassword")
                self.client.set_options(soapheaders=header)
                self.orgid = self.client.service.OrganizationQueryRoot()[0]
                self.orgidarray = self.client.factory.create(
                    'ArrayOfstring')
                self.orgidarray.string.append(self.orgid)
            except (ConfigParser.NoOptionError, AttributeError):
                raise
        except urllib2.URLError as e:
            raise Exception('Connection to %s failed. %s' % (url, e), sys.exc_info()[2])


class Member(object):
    def __init__(self, service):
        self.member = service.client.factory.create('Member')
        self.cmemail = service.client.factory.create('ContactMethodEmail')


class MemberRequest(object):
    def __init__(self, service, filename=None, action=None):
        self.service = service
        self.action = action
        self.majaction = self.action[0]
        if len(self.action) > 1:
            self.minaction = action[1]
        else:
            self.minaction = None
        self.filename = filename

        if self.majaction in ('QUERY', 'ADD', 'UPDATE', 'DELETE'):
            if self.majaction == 'QUERY':
                if self.minaction in ('MEMBERS', 'CMS', 'CFS'):
                    self.query(self.minaction)
                else:
                    print 'Invalid option. %s' % self.minaction

            if self.majaction == 'ADD':
                if self.filename is None:
                    print 'Must pass in a file when using ADD. eg. -f members.csv -a ADD'
                else:
                    self.add()

            if self.majaction == 'DELETE':
                if self.filename is None:
                    print 'Must pass in a file when using ADD. eg. -f members.csv -a DELETE'
                else:
                    self.delete()
        else:
            print '%s not a valid action.(QUERY, ADD, UPDATE, DELETE)' % self.majaction
            sys.exit()

    def query(self, minaction):
        if self.minaction == 'MEMBERS':
        # Writes out a JSON file of member login names and Id's to be deleted.
            if self.filename is None:
                print 'Must pass in a file to query members.  \
                eg. -f members.csv -a QUERY MEMBERS'
            else:
                self.reader = csv.DictReader(
                    open(self.filename, 'rU'))
                self.usernames = [
                    row['Username'] for row in self.reader]

                memberlist = []
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

                                memberlist.append(userdict)
                        except AttributeError as e:
                            print 'No Members found.'

                    if len(memberlist) > 0:
                        try:
                            with open('members.json', 'wa') as f:
                                f.write(json.dumps(memberlist, indent=4))

                            print 'members.json has been successfully written out.'
                        except IOError as e:
                            print e
                except suds.WebFault as e:
                    print e.fault.detail

        if self.minaction == 'CMS':  # Contact Methods
            cms = self.service.client.service.AvailableContactMethodQueryByOrganizationId(
                self.service.orgid)
            for cm in cms:
                strcm, cm = cm
                for c in cm:
                    print '%s_%s_%s (%s)' % (c.Transport,
                                             c.Qualifier,
                                             c.Ordinal,
                                             c.DisplayName)

        if self.minaction == 'CFS':  # Custom Fields
            cfs = self.service.client.service.OrganizationCustomFieldQueryByOrganizationId(
                self.service.orgidarray, 0, 300)
            for cf in cfs:
                strcf, cf = cf
                for c in cf:
                    print 'CF_%s' % (c.Name)

    def add(self):
        members = self.service.client.factory.create('ArrayOfMember')
        membermodel = Member(self.service)

        try:
            self.reader = csv.DictReader(open(self.filename, 'rU'))
            self.header = self.reader.fieldnames

            memberfields = []
            cmfields = []
            cffields = []
            cfdict = {}

            for attributes in membermodel.member:
                k, v = attributes
                memberfields.append(k)

            contactmethods = self.service.client.service.AvailableContactMethodQueryByOrganizationId(
                self.service.orgid)

            customfields = self.service.client.service.OrganizationCustomFieldQueryByOrganizationId(
                self.service.orgidarray, 0, 300)

            for cm in contactmethods:
                strcm, cm = cm
                for c in cm:
                    cmfields.append(
                        str('%s_%s_%s' % (c.Transport, c.Qualifier, c.Ordinal)))

            for cf in customfields:
                strcf, cf = cf
                for c in cf:
                    cffields.append('CF_%s' % (c.Name))
                    cfdict['CF_' + str(c.Name)] = c.OrganizationCustomFieldId
            print cfdict

            for row in self.reader:
                m = Member(self.service)
                cms = self.service.client.factory.create(
                    'ArrayOfContactMethod')
                cfs = self.service.client.factory.create(
                    'ArrayOfMemberCustomField')
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
                    if k in cffields:
                        cf = self.service.client.factory.create(
                            'MemberCustomField')
                        cf.Value = v
                        cf.OrganizationCustomFieldId = cfdict[k]
                        cfs.MemberCustomField.append(cf)

                    if k in memberfields:
                        m.member[k] = v
                        m.member.ContactMethods = cms
                        m.member.MemberCustomFields = cfs

                members.Member.append(m.member)
            print members

            try:
                print self.service.client.service.MemberCreate(members)
            except suds.WebFault as e:
                print e.fault.detail

        except IOError as e:
            print 'File %s not found.' % self.filename

    def update(self):
        pass

    def delete(self):
        try:
            self.memberids = json.load(open(self.filename, 'r'))
            for memberdict in self.memberids:
                try:
                    memberstring = self.service.client.factory.create(
                        'ArrayOfstring')
                    for k, v in memberdict.items():
                        memberstring.string.append(v)
                    print memberstring

                    confirmation = raw_input('Are you sure you want to delete %d users? yes/no: ' % len(
                        memberstring.string))
                    if confirmation == 'yes':
                        print "Processing Deletes..."
                        try:
                            print self.service.client.service.MemberDeleteById(
                                memberstring)
                        except suds.WebFault as e:
                            print e.fault.detail
                    else:
                        print 'Halting execution.  Exiting.'
                except Exception as e:
                    print e

        except ValueError:
            print 'Exiting. Not a valid JSON file.'


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

    try:
        service = Service()
        MemberRequest(service, args.file, args.action)
    except Exception as e:
    # except (urllib2.URLError, ConfigParser.NoOptionError, AttributeError) as e:
        print e

if __name__ == '__main__':
    main()
