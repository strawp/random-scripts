#!/usr/bin/env python
# Send an HTML email to all addresses in a txt file

import argparse
import sys
import smtplib, getopt, datetime, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage


parser = argparse.ArgumentParser(description="Wrapper for NTLM info leak and NTLM dictionary attack")
parser.add_argument("-e", "--emails", help="File containing list of email addresses")
parser.add_argument("-b", "--body", help="File containing HTML body of email")
parser.add_argument("-s", "--subject", help="Subject line of email")
parser.add_argument("-f", "--fromheader", help="From address")
args = parser.parse_args()

if not args.emails or not args.body or not args.subject or not args.fromheader:
  parser.print_usage()
  sys.exit(2)

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

  # Find any attachments and attach
  attachments = re.findall('src="cid:([^"]+)"',body)
  for attachment in attachments:
    fp = open( attachment, "rb" )
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', attachment )
    msg.attach(img)


  # Send email
  server = smtplib.SMTP('localhost')
  server.set_debuglevel(1)
  server.sendmail( fromheader, email, msg.as_string() )
  server.quit()

	
