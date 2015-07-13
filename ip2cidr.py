#!/usr/bin/python3

"""
Usage: ip2cidr.py input_file
Based on http://www.unix.com/shell-programming-and-scripting/233825-convert-ip-ranges-cidr-netblocks.html
"""

import sys, re, netaddr

def sanitize (ip):
	seg = ip.split('.')
	return '.'.join([ str(int(v)) for v in seg ])

# pointer to input file
fp_source = open(sys.argv[1], "r")

ptrnSplit = re.compile(' - | , ')

for line in fp_source:
	
	# parse on ' - ' et ' , '
	s = re.split(ptrnSplit, line)
	
	# sanitize ip: 001.004.000.107 --> 1.4.0.107 to avoid netaddr err.
	ip = [ sanitize(v) for v in s[:2] ]
	
	# conversion ip range to CIDR netblocks
	# single ip in range
	if ip[0] == ip[1]:
		print( ip[0])
		
	# multiple ip's in range
	else:
		ipCidr = netaddr.IPRange(ip[0], ip[1])
		for cidr in ipCidr.cidrs():
			print(cidr)

