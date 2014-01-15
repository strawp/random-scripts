#!/usr/bin/python
from __future__ import print_function
import argparse
import sys
import os.path

# Create a series of grep pipes to cut down a large dictionary of passwords to just ones relevant to a password policy

pipes = []


parser = argparse.ArgumentParser(description="Grep out a dictionary file")
parser.add_argument("-l", "--len", help="Minimum length of passwords")
parser.add_argument("-m", "--maxlen", help="Maximum length of passwords")
parser.add_argument("-e", "--excludelist", help="Exclude items from the specified word list")
parser.add_argument("-u", "--upper", action="store_true", help="Must contain an uppercase character")
parser.add_argument("-L", "--lower", action="store_true", help="Must contain a lowercase character")
parser.add_argument("-n", "--numbers", action="store_true", help="Must contain a number")
parser.add_argument("-s", "--special", action="store_true", help="Must contain at least one special (non-alphanumeric) character")
parser.add_argument("-S", "--specupnum", action="store_true", help="Must contain at least one special character, uppercase character or number")
parser.add_argument("-f", "--firstupper", action="store_true", help="First character is uppercase")
parser.add_argument("-r", "--norepeat", action="store_true", help="No repeating characters")
parser.add_argument("dictionary", help="Input dictionary file")
args = parser.parse_args()

if not args.dictionary:
  parser.print_usage()
  sys.exit(2)

if not os.path.isfile( args.dictionary ):
  print( "Not found: " + args.dictionary )
  sys.exit(2)

# Work out grep pipes
pipes.append( 'cat ' + args.dictionary )

if args.len:
  pipes.append( 'grep "^.\{'+str(int(args.len))+',\}$"' )

if args.maxlen:
  pipes.append( 'grep "^.\{,'+str(int(args.maxlen))+'\}$"' )

if args.excludelist:
  pipes.append( 'grep -x -v -F -f ' + args.excludelist )

if args.upper:
  pipes.append( 'grep "[A-Z]"' )

if args.lower:
  pipes.append( 'grep "[a-z]"' )

if args.numbers:
  pipes.append( 'grep "[0-9]"' )

if args.special:
  pipes.append( 'grep "[^a-zA-Z0-9]"' )

if args.specupnum:
  pipes.append( 'grep "\([^a-zA-Z0-9]\|[0-9]\|[A-Z]\)"' )

if args.firstupper:
  pipes.append( 'grep "^[A-Z]"' )

if args.norepeat:
  pipes.append( 'grep -v "\(.\)\\1"' )

# Construct command
cmd = " | ".join(pipes)
print("Running: " + cmd, end='\n', file=sys.stderr)

os.system( cmd )


