#!/usr/bin/env python
# Send an HTML email to all addresses in a txt file

import smtplib, getopt, datetime, re

def main(argv):
	emailsfile = ''
	bodyfile = ''
	subject = ''
	fromheader = ''
	try:
		opts, args = getopt.getopt( argv, "e:b:s:f:" )
	except getopt.GetoptError:
		print 'sendmails.py -e emailslist.txt -b mailbody.html -s subject -f fromaddress'
		sys.exit(2)
			
	for opt, arg in opts:
		if opt == "-e":
			emailsfile = arg
		elif opt == "-b":
			bodyfile = arg
		elif opt == "-s":
			subject = arg
		elif opt == "-f":
			fromheader = arg
			
	print 'Emails file: ', emailsfile
	print 'Body text file: ', bodyfile
	print 'Subject: ', subject
	print 'From: ', fromheader
	namematch = re.compile( "\w{2,}\.\w{2,}" )

	# Read in body
	with open (bodyfile,"r") as file:
		data = file.read().replace('\n','')
	
	# Read in emails
	with open(emailsfile) as f:
		emails = f.readlines()

	# Loop over emails
	for email in emails:
		
		email = email.strip()
		name = email.split('@')[0]
		if namematch.match( name ):
			name = name.replace("."," ").title()
		else:
			name = ''

		# Compile header
		header = "From: " + fromheader + "\r\nTo: " + email + "\r\nContent-Type: text/html; charset=UTF-8\r\nSubject: " + subject + "\r\n\r\n"

		# Compile body
		body = data.replace("{name}", name ).replace("{email}", email).replace("{date}",datetime.datetime.today().strftime("%d/%m/%Y"))
		
		# Send email
		server = smtplib.SMTP('localhost')
		server.set_debuglevel(1)
		server.sendmail( fromheader, email, header + body )
		server.quit()
	
if __name__ == "__main__":
	import sys
	main(sys.argv[1:])
	
