#!/usr/bin/python
import argparse
import sys
import os.path
import subprocess
import re

parser = argparse.ArgumentParser(description="Grep out info from the adobe creds file")
parser.add_argument("term", help="Search term")
parser.add_argument("creds", help="Adobe creds file")
args = parser.parse_args()

if not args.creds:
  parser.print_usage()
  sys.exit(2)

def parseline(line):
  # 103238704-|--|-jmyuncker@aol.com-|-r4Vp5iL2VbM=-|-maiden  name|--
  m = re.findall( '(([^\|]+)\|)', line )
  rtn = {}
  rtn['email'] = parsevalue(m[2][1])
  rtn['pass'] = parsevalue(m[3][1])
  rtn['hint'] = ''
  for i in range(4,len(m)):
    rtn['hint'] += parsevalue(m[i][1])+" "
  return rtn

def parsevalue(val):
  return re.sub('^-|-$','',val)

emaillist = []

print( 'Searching for '+args.term+' in '+args.creds+'...' )
sys.stdout.flush()

# First pass - get instances of term
result = subprocess.check_output( 'grep "' + args.term + '" ' + args.creds, shell=True )

print( 'Found ' + str(len(result.strip().split('\n'))) + ' results in search' )
print( result )
sys.stdout.flush()

for line in result.split('\n'):
  line = line.strip()
  if line == '':
    continue
  emaillist.append(parseline(line))


# Get unique list of passwords
passwords = {}
for info in emaillist:
  if not info['pass'] in passwords:
    if( info['pass'] != '' ):
      passwords[info['pass']] = []

print( 'Searching for shared passwords...' )
sys.stdout.flush()

# Iterate over passwords, finding all other people who have that password
for password in passwords.keys():
  print( 'Searching for ' + password + '...' )
  sys.stdout.flush()
  result = subprocess.check_output('grep "' + password + '" ' + args.creds, shell=True )
  print( 'Found ' + str(len(result.strip().split('\n'))) + ' uses' )
  sys.stdout.flush()
  for line in result.split('\n'):
    line = line.strip()
    if line == '':
      continue
    passwords[password].append(parseline(line))

print('')
print('Email addresses:')
print('================')
sys.stdout.flush()
for person in emaillist:
  print(person['email'])
  sys.stdout.flush()

print('')
print('Results:')
print('========')
sys.stdout.flush()

# Iterate over all people and output relevant password hints
for person in emaillist:
  if person['pass'] == '':
    continue;
  print('')
  print( person['email'] + ': ' + person['pass'] + ' ('+str(len(passwords[person['pass']]))+')' )
  for hint in passwords[person['pass']]:
    print( '  ' + hint['email'] + ': ' + hint['hint'] )
    sys.stdout.flush()


