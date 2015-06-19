#!/usr/bin/env python
# Send an HTML email to all addresses in a txt file

import argparse, sys, smtplib, datetime, re, os
from email import Encoders
from email.MIMEBase import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage
import time


parser = argparse.ArgumentParser(description="Wrapper for NTLM info leak and NTLM dictionary attack")
parser.add_argument("-e", "--emails", help="File containing list of email addresses")
parser.add_argument("-b", "--body", help="File containing HTML body of email")
parser.add_argument("-s", "--subject", help="Subject line of email")
parser.add_argument("-f", "--fromheader", help="From address")
parser.add_argument("-g", "--host", help="SMTP host")
parser.add_argument("-P", "--port", help="SMTP port")
parser.add_argument("-u", "--username", help="SMTP username")
parser.add_argument("-p", "--password", help="SMTP password")
parser.add_argument("-d", "--delay", help="Delay between mail sends (seconds)")
parser.add_argument("-a", "--attachment", help="Filename to add as an attachment")
args = parser.parse_args()

if not args.emails or not args.body or not args.subject or not args.fromheader:
  parser.print_usage()
  sys.exit(2)

if args.host and ( not args.username and not args.password ):
  print 'Username and password required when specifying host'
  sys.exit(2)
  if not args.port:
    args.port = 587

if args.delay:
  args.delay = int( args.delay )

if args.attachment:
  if not os.path.isfile(args.attachment):
    print 'Path to attachment ' + args.attachment + ' not found'

emailsfile = args.emails
bodyfile = args.body
subject = args.subject
fromheader = args.fromheader

print 'Emails file: ', emailsfile
print 'Body text file: ', bodyfile
print 'Subject: ', subject
print 'From: ', fromheader

namematch = re.compile( "\w{2,}\.\w{2,}" )
attachmentmatch = re.compile( 'src="cid:([^"]+)"' )

# Read in body
with open (bodyfile,"r") as file:
  data = file.read().replace('\n','')

# Read in emails
with open(emailsfile) as f:
  emails = f.readlines()

# Loop over emails
for email in emails:
  
  msg = MIMEMultipart()

  email = email.strip()
  name = email.split('@')[0]
  if namematch.match( name ):
    name = name.replace("."," ").title()
  else:
    name = ''

  # Compile header
  msg["From"] = fromheader
  msg["To"] = email
  msg["Subject"] = subject

  # header = "From: " + fromheader + "\r\nTo: " + email + "\r\nContent-Type: text/html; charset=UTF-8\r\nSubject: " + subject + "\r\n\r\n"

  # Compile body
  body = data.replace("{name}", name ).replace("{email}", email).replace("{date}",datetime.datetime.today().strftime("%d/%m/%Y"))
  msgText = MIMEText( body, "html" )
  msg.attach(msgText)

  # Find any embedded images and attach
  attachments = re.findall('src="cid:([^"]+)"',body)
  for attachment in attachments:
    fp = open( attachment, "rb" )
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', attachment )
    msg.attach(img)


  # Optional attachment
  if args.attachment:
    filename = os.path.basename( args.attachment )
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(args.attachment, "rb").read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="'+filename+'"')
    msg.attach(part)

  # Send email
  if not args.host:
    server = smtplib.SMTP('localhost')
  else:
    server = smtplib.SMTP(args.host, args.port)
    server.login(args.username, args.password)
  
  server.sendmail( fromheader, email, msg.as_string() )
  server.quit()

  if args.delay:
    time.sleep(args.delay)
	
