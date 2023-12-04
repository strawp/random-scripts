#!/usr/bin/python3
# Recursively examine SPF records for holes
# Requires "dig"

import argparse, sys, re, time, subprocess, json, netaddr

def get_dig_answer( domain, querytype ):
  rtn = []
  for line in subprocess.check_output(['dig',domain,querytype,'+noall','+answer']).decode('utf8').splitlines():
    if querytype == 'txt':
      m = re.findall('"([^"]+)"', line)
      s = ' '.join(m).strip().replace('  ',' ')
    else:
      m = re.search('([^ ]+)$', line)
      if not m: continue
      s = m.group(1)
    if querytype == 'mx':
      s = s.strip()[:-1]
    rtn.append(s)
  return rtn

def domain_exists( domain ):
  try:
    if 'NXDOMAIN' in subprocess.check_output(['host',domain]).decode('utf8'):
      return False
    return True
  except:
    print('Error looking up domain', domain)
    return False

def get_allowed_hosts( domain, recurse=True ):
  rtn = {domain:[]}
  hosts = []
  qualifiers = []
  modifiers = []
  for line in get_dig_answer(domain,'txt'):
    if 'v=spf' in line:
      # print(domain, line)
      for item in line.split(' '):
        item = item.lower()

        # Recurse into "include:" 
        if recurse and item.startswith('include:'):
          d = item.split(':')[1]
          hosts.append(get_allowed_hosts(d))

        # Recurse into "redirect="
        elif recurse and item.startswith('redirect='):
          d = item.split('=')[1]
          hosts.append(get_allowed_hosts(d))

        # Specified IP
        elif item.startswith('ip') or item.startswith('a:'):
          hosts.append(item)

        # References to other DNS records
        elif item == 'mx':
          hosts+= get_dig_answer( domain, 'mx' )

        elif item.split(':')[0] == 'ptr':
          t,d = item.split(':')
          hosts += get_allowed_hosts( d )

        elif item.startswith('mx:'):
          t,d = item.split(':')
          hosts+= get_dig_answer( d, 'mx' )

        # EXISTS
        elif item.startswith('exists:'):
          if not domain_exists( item.split(':')[1] ):
            item = '!' + item
          hosts.append( item )

        # Qualifiers
        elif item[0] in '+-~?':
          q = item[0]
          if q == '+':
            t = 'PASS'
          elif q == '?':
            t = 'NEUTRAL'
          elif q == '~':
            t = 'SOFTFAIL'
          elif q == '-':
            t = 'FAIL'
          qualifiers.append(t+': '+item)

        elif '=' in item:
          m = re.search('(.+)=(.+)', item)
          if m:
            modifiers.append( item )

        else:
          if recurse: print('WHAT:',item)

  rtn = {domain: {'hosts':hosts,'qualifiers':qualifiers,'modifiers':modifiers}}
  return rtn

def get_ips( allowlist ):
  rtn = []
  ipset = netaddr.IPSet()
  for domain, info in allowlist.items():
    for host in info['hosts']:
      if type( host ) is dict:
        rtn += get_ips( host )
      elif host.startswith('ip4:'):
        ipset.add(netaddr.IPNetwork(host.split(':')[1]))
  for ip in ipset:
    rtn.append( str( ip ) )
  rtn = sorted( list( set( rtn ) ) )
  return list( set( rtn ) )

def analyse( allowed, parentpath=[], parenthardfail=False ):
  for domain,info in allowed.items():
    hardfail = False
    score = 0
    issues = []
    for q in info['qualifiers']:
      if q.startswith('FAIL'): 
        hardfail = True
        break
      if q.startswith('NEUTRAL'):
        issues.append('[!] Neutral qualifier')
        score = 2
    
    if not hardfail and not parenthardfail:
      score = 1
      issues.append('[-] No hard fail')
    
    for host in info['hosts']:
      if type( host ) is dict:
        analyse( host, parentpath + [domain], parenthardfail or hardfail )
      else:
        if host.startswith('!exists'):
          score = 3
          issues.append('[!] UNREGISTERED DOMAIN')
    if score > 0:
      print('\nWeak SPF dependency (score '+str(score)+'):',' -> '.join(parentpath + [domain]))
      print(' - ' + '\n - '.join(issues))

def main():
  parser = argparse.ArgumentParser(description="Recursively scan SPF records for allowed IPs")
  parser.add_argument("--ips", action="store_true", help="Output an expanded list of all IP addresses allowed to send from this domain")
  parser.add_argument('-a',"--analyse", action="store_true", help="Find weak spots in the SPF records")
  parser.add_argument('-n',"--norecurse", action="store_true", help="Don't recurse through include: and redirect=")
  parser.add_argument("domain", help="email domain to scan from")
  args = parser.parse_args()
  
  allowed = get_allowed_hosts(args.domain, recurse=(not args.norecurse))
  
  # Output list of allowed IPs
  if args.ips:
    ips = get_ips( allowed )
    print( '\n'.join(ips) )
    sys.exit(0)
 
  if args.analyse:
    analyse( allowed )
    sys.exit(0)

  print(json.dumps(allowed,indent=2))

if __name__ == '__main__':
  main()
