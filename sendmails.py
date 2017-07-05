#!/usr/bin/env python
# Send an HTML email to all addresses in a txt file

import argparse, sys, smtplib, datetime, re, os, random, base64, time, subprocess #, html2text
from email import Encoders
from email.MIMEBase import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage

parser = argparse.ArgumentParser(description="Wrapper for NTLM info leak and NTLM dictionary attack")
parser.add_argument("-e", "--emails", help="File containing list of email addresses")
parser.add_argument("-E", "--email", help="Single email address to send to")
parser.add_argument("-b", "--body", help="File containing HTML body of email")
parser.add_argument("-t", "--text", action="store_true", help="Add a plain text part to the email converted from the HTML body (use if the target mail client doesn't display HTML inline, e.g. IBM Notes might not)")
parser.add_argument("-T", "--textfile", help="Add a plain text part to the email taken from the specified text file") 
parser.add_argument("-s", "--subject", help="Subject line of email")
parser.add_argument("-f", "--fromheader", help="From address (address or 'name <address>')")
parser.add_argument("-r", "--readreceipt", help="Read receipt address (same format as from/to headers")
parser.add_argument("-g", "--host", help="SMTP host")
parser.add_argument("-P", "--port", help="SMTP port")
parser.add_argument("-u", "--username", help="SMTP username")
parser.add_argument("-p", "--password", help="SMTP password")
parser.add_argument("-d", "--delay", help="Delay between mail sends (seconds)")
parser.add_argument("-a", "--attachment", help="Filename to add as an attachment")
parser.add_argument("-x", "--execute", action="append", help="Execute this command before sending each email (stack to create complex commands, e.g. -x 'script.sh' -x 'Email:{email}')")
args = parser.parse_args()

# Switch out place markers for variables
def compile_string(txt, name=None, fname=None, lname=None, email=None, user=None, randomint=None ):
  global intsfile
  txt = txt.replace("{name}", name )\
    .replace("{fname}", fname )\
    .replace("{lname}", lname )\
    .replace("{email}", email)\
    .replace("{username}", user)\
    .replace("{date}",datetime.datetime.today().strftime("%d/%m/%Y"))\
    .replace("{b64email}",base64.b64encode(email))\
    .replace("{b64remail}",base64.b64encode(email)[::-1])

  if re.search("{randomint}",txt):
    if not randomint:
      randomint = random.randint(1,9999999)
      print "Random integer: " + email + " : " + str(randomint)
    txt = txt.replace("{randomint}",str(randomint))
    randomints = True
    fp = open(intsfile,"a")
    fp.write(email + ":" + str(randomint)+'\n' )
    fp.close()
  return txt, randomint

if not ( args.body or args.textfile ) or not args.subject or not args.fromheader:
  parser.print_usage()
  sys.exit(2)

if not args.emails and not args.email:
  parser.print_usage()
  sys.exit(2)

# if args.host and ( not args.username and not args.password ):
#   print 'Username and password required when specifying host'
#   sys.exit(2)
#   if not args.port:
#     args.port = 587

if args.delay:
  args.delay = int( args.delay )

if args.attachment:
  if not os.path.isfile(args.attachment):
    print 'Path to attachment ' + args.attachment + ' not found'

if args.emails:
  emailsfile = args.emails
  print 'Emails file: ', emailsfile
else:
  print 'Email: ', args.email

subject = args.subject
fromheader = args.fromheader

if args.body:
  print 'Body text file: ', args.body
if args.textfile:
  print 'Flat text file: ', args.textfile
print 'Subject: ', subject
print 'From: ', fromheader

namematch = re.compile( "\w{2,}\.\w{2,}" )
attachmentmatch = re.compile( 'src="cid:([^"]+)"' )

# Read in body
if args.body:
  with open (args.body,"r") as file:
    html = file.read().replace('\n','')
else:
  html = None

# Read in flat text
if args.textfile:
  with open(args.textfile,'r') as f:
    text = f.read()
else:
  text = None

# Read in emails
if args.emails:
  with open(emailsfile) as f:
    emails = f.readlines()
else:
  emails = []
  emails.append(args.email)

# Connect
if not args.host:
  server = smtplib.SMTP('localhost')
else:
  server = smtplib.SMTP(args.host, args.port)
  if args.username and args.password: 
    server.login(args.username, args.password)

randomints = False
intsfile = "randomints.txt"
count = 0

# Loop over emails
for email in emails:
  
  msg = MIMEMultipart()
  randomint = None

  email = email.strip()
  user = email.split('@')[0]
  name = user
  if namematch.match( name ):
    name = name.replace("."," ").title()
  else:
    name = ''

  if len(name.split(' ')) >= 2:
    fname = name.split(' ')[0]
    lname = name.split(' ')[1]
  else:
    fname = ''
    lname = ''

  if args.execute:
    parts = []
    for x in args.execute:
      x,randomint = compile_string(x, name, fname, lname, email, user, randomint )
      parts.append(x)
    print 'Running: ' + ' '.join(parts)
    print subprocess.check_output(parts)

  # Compile header
  msg["From"] = fromheader
  msg["To"] = email
  msg["Subject"],randomint = compile_string(subject, name, fname, lname, email, user, randomint )
  if args.readreceipt: 
    print 'Adding read receipt header: ' + args.readreceipt
    msg["Disposition-Notification-To"] = args.readreceipt

  bodies = {}

  if html:
    bodies['html'] = html
  if text:
    bodies['text'] = text

  # Compile bodies
  for k,v in bodies.iteritems():
    v,randomint = compile_string(v, name, fname, lname, email, user, randomint )
    bodies[k] = v

  if 'html' in bodies.keys():
    msg.attach(MIMEText( bodies['html'], "html" ))
    if args.text:
      msg.attach(MIMEText(html2text.html2text(bodies['html']),'plain'))
  
    # Find any embedded images and attach
    attachments = re.findall('src="cid:([^"]+)"',bodies['html'])
    for attachment in attachments:
      fp = open( attachment, "rb" )
      img = MIMEImage(fp.read())
      fp.close()
      img.add_header('Content-ID', attachment )
      msg.attach(img)

  if 'text' in bodies.keys():
    msg.attach(MIMEText(bodies['text'],'plain'))

  # Optional attachment
  if args.attachment:
    filename = os.path.basename( args.attachment )
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(args.attachment, "rb").read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="'+filename+'"')
    msg.attach(part)

  # print msg.as_string()

  # Send email
  sys.stdout.write( "Sending to " + email + "... " )
  sys.stdout.flush()
  server.sendmail( fromheader, email, msg.as_string() )
  sys.stdout.write( "sent\n" )
  sys.stdout.flush()

  if args.delay:
    time.sleep(args.delay)
  count += 1 
  if count % 10 == 0:
    print 'Getting new connection...'
    server = smtplib.SMTP(args.host, args.port)
    if args.username and args.password: 
      server.login(args.username, args.password)
	
server.quit()

if randomints:
  print "Assigned random ints saved to " + intsfile
