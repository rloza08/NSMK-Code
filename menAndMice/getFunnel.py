#!/usr/bin/env python

#
# mmVLdefs.py - dump VLAN defs from Men & Mice
#               written using soapCLI.py as example
#

import os
import re
import suds
from suds import *
from suds.plugin import MessagePlugin
import auto_logger as l

class mmSoap(client.Client):
    """
    A module that eases the usage of the Men and Mice SOAP API.

    Start by creating the client:
        cli = mmSoap(proxy=<M&M web server>,server=<M&M Central server>,username=<user name>,password=<password>)

    For help of the cli client object, type:
        cli.help()

    """

    def __init__(self, proxy='localhost',server='localhost',platform='windows',https=False,
                 username=None,password=None,namespace=None,verifySSL=True,**kw):
        class EnvelopeFixer(MessagePlugin):
            def marshalled(self, context):
                root = context.envelope.getRoot()
                envelope = root.getChild("Envelope")
                envelope.getChildren()[1].setPrefix("SOAP-ENV")
                # print envelope.getChildren()[1]
                return context

        if platform == 'unix':
            url = "http://" + proxy + ":8111/Soap?WSDL?server=" + server
            location = "http://" + proxy + ":8111/Soap?"
        elif platform == 'windows':
            url = 'http://' + proxy + '/_mmwebext/mmwebext.dll?WSDL?server=' + server
            location = 'http://' + proxy + '/_mmwebext/mmwebext.dll?Soap'
        else:
            print ('Platform not known. Known platforms are "unix" and "windows"')
            return

        if https:
            url=url.replace('http://','https://')
            location=location.replace('http://','https://')
            if verifySSL is False:
                ssl._create_default_https_context = ssl._create_unverified_context

        if namespace:
            url=url+'?ns='+namespace

        kw['plugins']=[EnvelopeFixer()]
        kw['location']=location
        client.Client.__init__(self,url,**kw)

        self._url=url
        self._proxy=proxy
        self._server=server
        self._username=username
        self._password=password
        self._session=None
        self._errNetObjHandler='Unable to complete operation. Netobject handler not running'
        self._errInvalidSession='Invalid or expired session'
        self.login(server=server,username=username,password=password)

    def __getattr__(self,name):
        self._operation=name
        return self


    def __call__(self,operation=None,*args,**kw):
        kw['session']=self._session
        if operation==None: operation = self._operation

        try:
            return getattr(self._client.service,operation)(*args,**kw)
        except suds.WebFault as e:
            if self._session is not None and (self._errInvalidSession in str(e) or self._errNetObjHandler in str(e)):
                print('Trying to log in again because: ' + str(e))
                self.login()
                kw['session']=self._session
                return getattr(self._client.service,operation)(*args,**kw)
            else:
                raise

    def __checkLogin(self):
        if self._session == None:
            print("You are not logged in. ")

    def login(self,server=None,username=None,password=None):
        if server==None:
            server=self._server
            print('Server: ' + server)
        if username==None:
            username = self._username
            print('Username: ' + username)
        if password==None:
            password = self._password

        self._session=self.Login(server=self._server,loginName=username,password=password)
        return self._session

    def logout(self):
        self.Logout()

    def _getServices(self,theFilter=None):
        outString = ''
        for commandObj in self.sd[0].ports[0][1]:
            command = commandObj[0]
            if theFilter is not None and theFilter.lower() not in command.lower():
                continue
            theSpace='       '
            outString += command + '(\n'

            for param in commandObj[1]:
                paramName = param[0]
                if paramName == 'session':
                    continue
                paramType = param[1].type[0]
                reqnill=[]
                if param[1].required():
                    reqnill.append('required')
                else:
                    reqnill.append('optional')
                if param[1].nillable:
                    reqnill.append('nillable')
                else:
                    reqnill.append('non-nillable')
                reqnill =  '\n' if len(reqnill)==0 else '   [' + ', '.join(reqnill) + ']\n'
                theComma = ',' if param is not commandObj[1][-1] else ''
                outString += theSpace + paramType + '  ' + paramName + theComma + reqnill

            outString += ')\n\n'

        if outString is '':
            outString = 'No mathing service found\n'
        return outString

    def _getObjects(self,theFilter=None):
        allTypes = []
        for type in cli.sd[0].types:
            if theFilter is not None and theFilter.lower() not in type[0].name.lower():
                continue
            allTypes.append(str(self.factory.create(type[0].name)))
        return '\n'.join(allTypes)

    def __str__(self):
        return self._getServices()

    def services(self,theFilter=None):
        print(self._getServices(theFilter))

    def objects(self,theFilter=None):
        print(self._getObjects(theFilter))

    def create(self,name):
        return self.factory.create(name)

class getFunnel(object):
    def __init__(self):
        try:
            #user = os.environ.get("SOAP_USER", None)
            user = "opsware1"
            #password = os.environ.get("SOAP_PWD", None)
            password = "0psware1!"
            self.cli = mmSoap(proxy="dnstool", server="dnstool",
                              username=user, password=password,
                              namespace="mm", cache=None)
        except Exception as exception:
            print('Could not login into men and mice.')
            print('Details:',exception)
            os._exit(-1)
        self.vlanRaw = "funnel.raw"
        self.vlanCsv = "funnel.csv"

    def dumpRaw(self):
        vdat = self.cli.executePreparedStatement(name='getFunnelVLANs', params=[])
        f = open(self.vlanRaw, "w")
        f.write(str(vdat))
        f.close()

    def parseRAW(self):
        ifil = open(self.vlanRaw, "r")
        ofil = open(self.vlanCsv, "w")
        row = []

        vNum = re.compile('\d+$')

        for line in ifil:
            if ',' not in line:
                continue

            if '},' in line:
                m = vNum.match(row[0])
                if m:
                    v = re.match(r"NET", row[2])
                    if v:
                        ofil.write("%s,%s,%s\n" % (row[0], row[2], row[1]))

                row = []
                continue

            line = re.sub(r'^\s+|,|"', '', line.rstrip())
            m = re.match(r"10.x.[a-h]", line)
            if m:
                line = re.sub(r'10.x.', 'net', line.rstrip())
                line = line.upper()

            row.append(line)

        ifil.close()
        ofil.close()


        def isList(self, invar):
            # start Men & Mice code
            if isinstance(invar, type([])):
                return True
            else:
                return False

if __name__ == '__main__':
    try:
        obj = getFunnel()
        obj.dumpRaw()
        obj.parseRAW()
        print ("men and mice backend: got funnel.")
    except Exception as err:
        print ("men and mice backend: failed getting funnel.")