import requests
import argparse
import sys
from texttable import Texttable

__author__ = '@2xxeformyshirt'
__version__ = '1.0.0'

parser = argparse.ArgumentParser()
parser.add_argument('-t',dest='target',type=str,required=True,help='target domain')
parser.add_argument('-a',dest='apikey',type=str,required=False,help='Hunter.io API key') 
parser.add_argument('-l',dest='apilist',type=str,required=False,help='file of API keys')
parser.add_argument('-o',dest='outputfile',type=str,required=True,help='Output file location')
parser.add_argument('-f','--free',dest='freetier',action='store_true',required=False,help='Enable free tier limit restrictions')
parser.add_argument('-p','--print',dest='printtable',action='store_true',required=False,help='print a text table of the results')
args = vars(parser.parse_args())

if len(sys.argv) == 1:
    print '[-] Missing arguments...quitting!'
    sys.exit()

BANNER=''' /\___/\  
|       | Quiver
 \     /  
  |___|   @2xxeformyshirt
 
'''

class Prey():
    def __init__(self,fn,ln,em):
        self.fn = fn
        self.ln = ln
        self.em = em

class HunterKey():
    def __init__(self,key,stamina):
        self.key = key
        self.stamina = stamina

class HunterManager():
    def __init__(self,args):
        '''exit if api key and API file are both supplied or neither are supplied
           check stamina (number of requests left) of each key'''
        self.kt = 0
        if args['apikey'] is None and args['apilist'] is None:
            print '[-] Missing API input...quitting!'
            sys.exit()
        elif args['apikey'] is not None and args['apilist'] is not None:
            print '[-] Too many API inputs...quitting!'
            sys.exit()
        elif args['apikey'] is not None:
            self.kt = self.checkkeystatus(args['apikey'])
            if self.kt <= 0:
                print '[-] Key has no stamina...quitting!'
                sys.exit()
            self.apikey = HunterKey(args['apikey'],kr)
        elif args['apilist'] is not None:
            self.apilist = []
            with open(args['apilist'],'r') as f:
                for key in f.readlines():
                    kr = self.checkkeystatus(key.strip())
                    if kr > 0:
                        self.apilist.append(HunterKey(key.strip(),kr))
                    else:
                        print '[-] Key %s exhausted' % key.strip()
            if len(self.apilist) == 0:
                print '[-] Not API keys found in file'
                sys.exit()
            for k in self.apilist:
                self.kt = self.kt + k.stamina
            if self.kt <= 0:
                print '[-] Keys have no stamina...quitting!'
                sys.exit()
            self.apikey = self.apilist[0]
            self.multikey = True
            
        self.target = args['target']
        self.outputfile = args['outputfile']
        self.freetier = args['freetier']
        self.people = []
        self.apilistall = self.apilist

    def checkkeystatus(self,key):
        '''check the number of requests a key can make before being exhausted'''
        url = 'https://api.hunter.io/v2/account?api_key=%s' % key
        r = requests.get(url)
        if str(r.status_code)[:1] != '2':
            print '[-] Error calling Hunter.io API...quitting!'
            sys.exit()
        return (r.json()['data']['calls']['available']  - r.json()['data']['calls']['used'])

    def rotatekey(self):
        if len(self.apilist) == 0:
            print '[-] All keys exhausted...quitting!'
            sys.exit()
        else:
            self.apilist.pop(0)
            self.apikey = self.apilist[0]

    def apirequest(self,offset):
        '''request maximum number of usernames for a single request (100)'''

        if self.apikey.stamina == 0:
            print '[-] Key %s exhausted' % self.apikey.key
            if self.multikey:
                self.rotatekey()

        url = 'https://api.hunter.io/v2/domain-search?domain=%s&api_key=%s&limit=100&offset=%s' % (self.target,self.apikey.key,str(offset))
        r = requests.get(url)
        if str(r.status_code)[:1] != '2':
            print '[-] Error calling Hunter.io API...quitting!'
            sys.exit()
        
        '''reduce stamina by 1 (note: responses with status=400 do not decrement stamina)'''
        self.apikey.stamina = self.apikey.stamina - 1
        return r.json()
        
    def appendperson(self,of,rjson):
        '''extracts firstname, lastname, and email from json and adds to list'''
        for prey in rjson['data']['emails']:
            p = Prey(prey['first_name'],prey['last_name'],prey['value'])
            line = '%s,%s,%s\n' % (p.fn,p.ln,p.em)
            of.write(line)
            self.people.append(p)

def main(args):
    print BANNER
    hunter = HunterManager(args)
    print '[+] Hunting for users associated with %s' % hunter.target

    '''determine if number of results is within free tier limit
       quit if not within free tier limit and switch set'''
    rjson = hunter.apirequest(0)
    maxemails = rjson['meta']['results']
    numreq = maxemails/100
    if maxemails % 100 != 0:
        numreq = numreq + 1
    if hunter.freetier:
        if numreq > 100:
            print '[-] Number of requests exceeds free tier limit...quitting!'
            sys.exit()    

    '''quit if there isnt enough key stamina to fulfill all requests'''
    if hunter.kt < numreq:
        print '[-] Not enough stamina to fulfill requests'
        sys.exit()

    '''start writing ouput'''
    of = open(hunter.outputfile,'w+')
    of.write('First,Last,Email\n')

    '''add emails from original request to list'''
    hunter.appendperson(of,rjson)

    '''request remaining people'''
    i = 1
    while i < numreq:
        rjson = hunter.apirequest(i*100)
        hunter.appendperson(of,rjson)
        i = i + 1
    print '[+] Results written to %s\n' % hunter.outputfile

    '''print table of people'''
    if args['printtable']:
        table1 = Texttable()
        table1.set_deco(Texttable.HEADER)
        table1.set_cols_align(['l', 'l', 'l'])
        table1.add_row(['First Name','Last Name','Email'])
        for person in hunter.people:
            table1.add_row([person.fn,person.ln,person.em])
        print '[+] Printing results:'
        print table1.draw()+'\n'

    '''write out status of each key'''
    table2 = Texttable()
    table2.set_deco(Texttable.HEADER)
    table2.set_cols_align(['l', 'l'])
    table2.add_row(['Key','Stamina'])
    for k in hunter.apilistall:
        ks = hunter.checkkeystatus(k.key)
        table2.add_row([k.key,ks])
    print '[+] Retrieving new staminas:'
    print table2.draw()+'\n'

if __name__ == '__main__':
    try:
        main(args)
    except KeyboardInterrupt:
        print '[-] User interrupt...quitting!'
        sys.exit()