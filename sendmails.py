#!/usr/bin/env python
# Send an HTML email to all addresses in a txt file

import argparse, sys, smtplib, datetime, re, os, random, base64, time, subprocess, csv, html2text
from email import encoders
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage

varnames = ['email','name','fname','lname','user']
markers = []
markers.extend(varnames)
markers.extend(['date','b64email','b64remail','randomint'])


class Sendmails:

  host = None
  port = None
  ews = None
  username = None
  password = None
  recipients = []
  html = None
  dtformat = None
  text = None
  subject = None
  fromheader = None
  readreceipt = None
  headers = []
  delay = None
  reconnect = None
  attachments = []
  execute = []
  templates = []
  server = None
  session = None
  emailindex = 1

  # Connect to SMTP server
  def connect( self ):
    if self.ews:
      return True
    print('Getting new connection...')
    if not self.host:
      self.server = smtplib.SMTP('localhost')
    else:
      self.server = smtplib.SMTP(self.host, self.port)
      try:
        self.server.starttls()
      except:
        print('Server doesn\'t support STARTTLS')
      self.server.ehlo()
      if self.username and self.password: 
        self.server.login(self.username, self.password)
    return True

  def disconnect( self ):
    if self.ews:
      return True
    self.server.quit()

  def run( self ):

    # Connect
    self.connect()

    randomints = False
    intsfile = "randomints.txt"
    count = 0

    # Loop over emails
    for variables in self.recipients:
      e = Email( variables )
      e.subject = self.subject
      e.fromheader = self.fromheader  
      e.variables['dtformat'] = self.dtformat
      e.readreceipt = self.readreceipt
      e.addtext = self.addtext
      e.attachments = self.attachments

      # Other custom headers
      for h in self.headers:
        k,v = h.split(':')
        e.headers[k.strip()] = v.strip()

      # Set email body
      if self.html:
        e.html = self.html
      if self.text:
        e.text = self.text
      if self.templates:
        tmpl = self.templates[count%len(self.templates)]
        e.html = tmpl['content']
        print('Using template: ' + tmpl['name'])
      
      e = self.compile( e )
      
      if e.usesrandomint:
        fp = open(intsfile,"a")
        fp.write(e.variables['email'] + ":" + str(e.randomint)+'\n' )
        fp.close()
        randomints = True

      # Send email
      self.send( e )

      if self.delay:
        time.sleep(self.delay)
      count += 1 
      if count % int(self.reconnect) == 0:
        self.connect() 
    
    self.disconnect()

    if randomints:
      print("Assigned random ints saved to " + intsfile)


  def compile( self, email ):
    if self.execute:
      parts = []
      for x in self.execute:
        x = email.compile_string(x)
        parts.append(x)
      print('Running: ' + ' '.join(parts))
      print(subprocess.check_output(parts))

    # Compile header
    email.subject = email.compile_string(email.subject)
    
    # Compile bodies
    if email.html:
      email.html = email.compile_string( email.html )
    if email.text:
      email.text = email.compile_string( email.text )
    else:
      email.text = html2text.html2text( email.html )
    return email

  def send( self, email ):
    sys.stdout.write( "[" + str(self.emailindex) + "/" + str(len(self.recipients))+ "] Sending to " + email.variables['email'] + "... " )
    self.emailindex += 1
    sys.stdout.flush()
    if self.ews:
      self.send_ews( email )
    else:
      self.send_smtp( email )
    sys.stdout.write( "sent ["+datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')+"]\n" )
    sys.stdout.flush()

  def send_smtp( self, email ):
    if not self.server:
      self.connect()
    msg = email.get_mimemultipart()
    try:
      self.server.sendmail( email.fromheader, email.variables['email'], msg.as_string() )
    except e:
      if self.delay:
        time.sleep(self.delay)
      send_smtp( email )
    return True

  def send_ews( self, email ):
    from exchangelib import Account, Message, Mailbox, FileAttachment, HTMLBody, Credentials, Configuration, NTLM, DELEGATE
    creds = Credentials(self.username,self.password)
    config = Configuration(
      service_endpoint=self.ews, 
      credentials=creds, 
      auth_type=NTLM
    )
    account = Account(
        primary_smtp_address=self.username,
        config=config, 
        autodiscover=False,
        access_type=DELEGATE,
    )
    m = email.get_ewsmessage( account )
    m.send()
    return False

class Email:
  variables = {}
  toheader = None
  fromheader = None
  subject = None
  html = None
  text = None
  addtext = False
  randomint = None
  usesrandomint = False
  readreceipt = None
  attachments = []
  headers = {}

  def __init__( self, variables ):
    self.toheader = variables['email']
    msg = MIMEMultipart()
    self.randomint = random.randint(1,9999999)
    self.variables = {}

    for k,v in variables.items():
      self.variables[k] = v

    namematch = re.compile( r'\w{2,}\.\w{2,}' )
    self.variables['email'] = self.toheader.strip()
    self.variables['user'] = self.variables['email'].split('@')[0]
    if 'name' not in list(self.variables.keys()) or self.variables['name'] == '':
      if namematch.match( self.variables['user'] ):
        self.variables['name'] = self.variables['user'].replace("."," ").title()
      else:
        self.variables['name'] = ''

    if len(self.variables['name'].split(' ')) >= 2:
      if 'fname' not in list(self.variables.keys()): self.variables['fname'] = self.variables['name'].split(' ')[0]
      if 'lname' not in list(self.variables.keys()): self.variables['lname'] = self.variables['name'].split(' ')[1]
    else:
      if 'fname' not in list(self.variables.keys()): self.variables['fname'] = ''
      if 'lname' not in list(self.variables.keys()): self.variables['lname'] = ''
    
    # print( self.variables )
  
  # Switch out place markers for variables
  def compile_string( self, txt ):
    for name,val in self.variables.items():
      if type(val) == None: continue
      txt = txt.replace('{'+name+'}', str(val) )

    txt = txt\
      .replace("{date}",datetime.datetime.today().strftime(self.variables['dtformat']))\
      .replace("{b64email}",str(base64.b64encode(self.variables['email'].encode('utf-8'))))\
      .replace("{b64remail}",str(base64.b64encode(self.variables['email'].encode('utf-8'))[::-1]))
    
    if re.search('{randomint}', txt ):
      txt = txt.replace("{randomint}",str(self.randomint))
      self.usesrandomint = True
    return txt

  def get_mimemultipart( self ):
    msg = MIMEMultipart()
    msg['From'] = self.fromheader
    msg['To'] = self.toheader
    msg['Subject'] = self.subject
    if self.readreceipt:
      msg["Disposition-Notification-To"] = self.readreceipt
    for k,v in self.headers:
      msg[k] = v
    
    if self.html:
      msg.attach(MIMEText( self.html, "html" ))
    # if self.text:
    #   msg.attach(MIMEText(html2text.html2text(self.text),'plain'))
    
      # Find any embedded images and attach
      attachments = re.findall( 'src="cid:([^"]+)"', self.html )
      for attachment in attachments:
        fp = open( attachment, "rb" )
        img = MIMEImage(fp.read())
        fp.close()
        img.add_header('Content-ID', attachment )
        msg.attach(img)

    # Optional attachment
    for a in self.attachments:
      filename = os.path.basename( a )
      part = MIMEBase('application', "octet-stream")
      part.set_payload(open(a, "rb").read())
      encoders.encode_base64(part)
      part.add_header('Content-Disposition', 'attachment; filename="'+filename+'"')
      msg.attach(part)
    
    return msg

  def get_ewsmessage( self, account ):
    from exchangelib import Account, Message, Mailbox, FileAttachment, HTMLBody, Credentials, Configuration, NTLM, DELEGATE
    m = Message(
      account=account,
      subject=self.subject,
      body=HTMLBody(self.html),
      to_recipients=[self.toheader]
    )
    if self.readreceipt:
      m.is_read_receipt_requested = True
  
    if len( self.headers ) > 0:
      print('Custom mail headers not currently supported in EWS mode')
    # for k,v in self.headers:
    # This is fiddly, not enabled yet

    # Find any embedded images and attach
    attachments = re.findall( 'src="cid:([^"]+)"', self.html )
    for attachment in attachments:
      a = FileAttachment(
        name=attachment,
        content=open(attachment, "rb").read(),
        is_inline=True,
        content_id=attachment
      )
      m.attach(a)

    # Optional attachment
    for attachment in self.attachments:
      a = FileAttachment(
        name=attachment,
        content=open(attachment, "rb").read()
      )
      m.attach(a)
    return m

def main():
  parser = argparse.ArgumentParser(description="Send emails with various helpful options")
  parser.add_argument("-e", "--emails", help="File containing list of email addresses")
  parser.add_argument("-E", "--email", help="Single email address to send to")
  parser.add_argument("--csv", help="CSV file of email addresses with headers containing at least 'email' and optionally also: '"+"', '".join(varnames)+"'")
  parser.add_argument("-b", "--body", help="File containing HTML body of email, can contain template markers to be replaced with each email sent: {"+"}, {".join(markers)+"}")
  parser.add_argument("-B", "--bodydir", help="Directory containing any number of .html files which will be cycled through (different template for each email) to act as the body template")
  parser.add_argument("--dtformat", default="%d/%m/%Y", help="Format string for using when substituting {date} in templates")
  parser.add_argument("-t", "--text", action="store_true", help="Add a plain text part to the email converted from the HTML body (use if the target mail client doesn't display HTML inline, e.g. IBM Notes might not)")
  parser.add_argument("-T", "--textfile", help="Add a plain text part to the email taken from the specified text file") 
  parser.add_argument("-s", "--subject", help="Subject line of email")
  parser.add_argument("-f", "--fromheader", help="From address (address or 'name <address>')")
  parser.add_argument("-r", "--readreceipt", help="Read receipt address (same format as from/to headers")
  parser.add_argument("-H", "--header", action="append", help="Add any number of custom headers")
  parser.add_argument("-g", "--host", help="SMTP host")
  parser.add_argument("-P", "--port", help="SMTP port")
  parser.add_argument("-u", "--username", help="SMTP / EWS username")
  parser.add_argument("-p", "--password", help="SMTP / EWS password")
  parser.add_argument("--ews", help="URL to EWS endpoint (e.g. https://owa.example.com/EWS/Exchange.asmx)")
  parser.add_argument("-d", "--delay", help="Delay between mail sends (seconds)")
  parser.add_argument("--reconnect", default=5, type=int, help="Reconnect to SMTP host after this many email sends")
  parser.add_argument("-a", "--attachment", help="Filename to add as an attachment")
  parser.add_argument("-x", "--execute", action="append", help="Execute this command before sending each email (stack to create complex commands, e.g. -x 'script.sh' -x 'Email:{email}')")
  args = parser.parse_args()
  
  if not ( args.body or args.bodydir or args.textfile ) or not args.subject or ( not args.ews and not args.fromheader):
    parser.print_usage()
    sys.exit(2)

  if not args.emails and not args.email and not args.csv:
    parser.print_usage()
    sys.exit(2)

  sender = Sendmails()

  if args.host and not args.port:
    args.port = 587
  sender.port = args.port
  sender.host = args.host
  if args.ews: 
    sender.ews = args.ews
    if args.fromheader:
      print('NOTE: The "From:" header can\'t be spoofed over EWS')
    
    if args.text or args.textfile:
      print('NOTE: EWS methods are currently HTML only')

  if args.dtformat: sender.dtformat = args.dtformat
  sender.reconnect = args.reconnect

  sender.username = args.username
  sender.password = args.password

  if args.delay:
    args.delay = int( args.delay )
  sender.delay = args.delay

  if args.attachment:
    if not os.path.isfile(args.attachment):
      print('Path to attachment ' + args.attachment + ' not found')
    else:
      sender.attachments.append( args.attachment )

  sender.execute = args.execute

  if args.emails:
    emailsfile = args.emails
    print('Emails file: ', emailsfile)
  elif args.email:
    print('Email: ', args.email)
  elif args.csv:
    print('CSV: ', args.csv)


  # Dictionary specific to an email
  variables = {}

  sender.subject = args.subject
  sender.fromheader = args.fromheader

  if args.body:
    print('Body text file: ', args.body)
  if args.textfile:
    print('Flat text file: ', args.textfile)
  print('Subject: ', args.subject)
  print('From: ', args.fromheader)

  attachmentmatch = re.compile( 'src="cid:([^"]+)"' )

  # Read in body
  if args.body:
    with open (args.body,"r") as file:
      html = file.read() # .replace('\n','')
  else:
    html = None
  sender.html = html

  # Read in array of bodies
  templates = None
  if args.bodydir:
    bd = os.path.expanduser(args.bodydir)
    if not os.path.isdir( bd ):
      print("FAIL: " + bd + " doesn't exist")
    files = [f for f in os.listdir(bd) if os.path.isfile(os.path.join(bd,f))]  # and (re.match('.+\.html$',f) != None ))]
    files = [f for f in files if re.match('.+\.html$',f) != None]
    files.sort()
    templates = []
    for fn in files:
      fn = os.path.join(bd,fn)
      with open(fn,'r') as f:
        templates.append({'name':fn,'content':f.read()})

    if len( templates ) == 0:
      print('FAIL: No html files found in ' + bd)
    sender.templates = templates

  # Read in flat text
  if args.textfile:
    sender.addtext = True
    with open(args.textfile,'r') as f:
      text = f.read()
  else:
    text = None
  sender.addtext = args.text
  sender.text = text

  # Read in emails
  recipients = []
  if args.csv:
    with open(args.csv, 'r') as csvfile:
      csvreader = csv.DictReader(csvfile)
      for row in csvreader:
        for k in list(row.keys()):
          if k not in markers: markers.append(k)
        if 'email' not in list(row.keys()): continue
        recipients.append( row )
    
  elif args.emails:
    with open(emailsfile) as f:
      emails = f.readlines()
    for email in emails:
      email = email.strip()
      recipients.append({'email':email})
  else:
    recipients.append({'email':args.email})
  sender.recipients = recipients
  sender.run()

if __name__ == "__main__":
  main()

