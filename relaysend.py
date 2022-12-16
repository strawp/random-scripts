#!/usr/bin/env python
# Test if an SMTP service supports open relay

import argparse, sys, smtplib, datetime, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage


parser = argparse.ArgumentParser(description="Test if an SMTP service supports open relay")
parser.add_argument("-t", "--toheader", help="To address")
parser.add_argument("-f", "--fromheader", help="From address")
parser.add_argument("-c", "--ccheader", help="CC address")
parser.add_argument("-g", "--host", help="SMTP host")
parser.add_argument("-m", "--message", help="An optional message to append to the generated email")
args = parser.parse_args()

if not args.toheader or not args.fromheader or not args.host:
  parser.print_usage()
  sys.exit(2)

print('From: ', args.fromheader)
print('To: ', args.toheader)
print('CC: ', args.ccheader)
print('Host: ', args.host)
if args.message:
  print('Message: ', args.message)

msg = MIMEMultipart()

# Compile header
msg["From"] = args.fromheader
msg["To"] = args.toheader
msg["Cc"] = args.ccheader
msg["Subject"] = "Relayed mail from " + args.host

# Compile body
html = "<p>This email has been sent via an open relay at <strong>"+args.host+"</strong></p>"
if args.message:
  html += "<p>" + args.message + "</p>"
msgText = MIMEText( html, "html" )
msg.attach(msgText)

# Send email
server = smtplib.SMTP(args.host)
server.set_debuglevel(1)
server.sendmail( args.fromheader, args.toheader, msg.as_string() )
server.quit()

print('Done')
	
