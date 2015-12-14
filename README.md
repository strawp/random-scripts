# Random Scripts

## adobe-grepper.py 

    usage: adobe-grepper.py [-h] term creds
    
    Grep out info from the adobe creds file
    
    positional arguments:
      term        Search term
      creds       Adobe creds file
    
    optional arguments:
      -h, --help  show this help message and exit

## cidrdiff.py 


## dictionary-grepper.py 

    usage: dictionary-grepper.py [-h] [-l LEN] [-m MAXLEN] [-e EXCLUDELIST] [-u]
                                 [-L] [-a] [-n] [-s] [-S] [-f] [-r]
                                 dictionary
    
    Grep out a dictionary file
    
    positional arguments:
      dictionary            Input dictionary file
    
    optional arguments:
      -h, --help            show this help message and exit
      -l LEN, --len LEN     Minimum length of passwords
      -m MAXLEN, --maxlen MAXLEN
                            Maximum length of passwords
      -e EXCLUDELIST, --excludelist EXCLUDELIST
                            Exclude items from the specified word list
      -u, --upper           Must contain an uppercase character
      -L, --lower           Must contain a lowercase character
      -a, --letter          Must contain an upper or lower case letter
      -n, --numbers         Must contain a number
      -s, --special         Must contain at least one special (non-alphanumeric)
                            character
      -S, --specupnum       Must contain at least one special character, uppercase
                            character or number
      -f, --firstupper      First character is uppercase
      -r, --norepeat        No repeating characters

## ip2cidr.py 


## ntlm-botherer.py 

    usage: ntlm-botherer.py [-h] [-u USER] [-U USERLIST] [-p PASSWORD] [-d DOMAIN]
                            [-P PASSLIST] [-D DELAY] [-i] [-l] [-s] [-b] [-1]
                            url
    
    Wrapper for NTLM info leak and NTLM dictionary attack
    
    positional arguments:
      url                   URL of NTLM protected resource
    
    optional arguments:
      -h, --help            show this help message and exit
      -u USER, --user USER  Username to dictionary attack as
      -U USERLIST, --userlist USERLIST
                            Username list to dictionary attack as
      -p PASSWORD, --password PASSWORD
                            Password to dictionary attack as
      -d DOMAIN, --domain DOMAIN
                            NTLM domain name to attack
      -P PASSLIST, --passlist PASSLIST
                            Password list to dictionary attack as
      -D DELAY, --delay DELAY
                            Delay between each attempt, in seconds
      -i, --info            Exploit NTLM info leak
      -l, --login           Test logins (requires username and passwords)
      -s, --same            Try password=username
      -b, --blank           Try blank password
      -1, --quitonsuccess   Stop as soon as the first credential is found

## relaysend.py 

    usage: relaysend.py [-h] [-t TOHEADER] [-f FROMHEADER] [-g HOST]
    
    Wrapper for NTLM info leak and NTLM dictionary attack
    
    optional arguments:
      -h, --help            show this help message and exit
      -t TOHEADER, --toheader TOHEADER
                            To address
      -f FROMHEADER, --fromheader FROMHEADER
                            From address
      -g HOST, --host HOST  SMTP host

## sendmails.py 

    usage: sendmails.py [-h] [-e EMAILS] [-b BODY] [-s SUBJECT] [-f FROMHEADER]
                        [-g HOST] [-P PORT] [-u USERNAME] [-p PASSWORD] [-d DELAY]
                        [-a ATTACHMENT]
    
    Wrapper for NTLM info leak and NTLM dictionary attack
    
    optional arguments:
      -h, --help            show this help message and exit
      -e EMAILS, --emails EMAILS
                            File containing list of email addresses
      -b BODY, --body BODY  File containing HTML body of email
      -s SUBJECT, --subject SUBJECT
                            Subject line of email
      -f FROMHEADER, --fromheader FROMHEADER
                            From address
      -g HOST, --host HOST  SMTP host
      -P PORT, --port PORT  SMTP port
      -u USERNAME, --username USERNAME
                            SMTP username
      -p PASSWORD, --password PASSWORD
                            SMTP password
      -d DELAY, --delay DELAY
                            Delay between mail sends (seconds)
      -a ATTACHMENT, --attachment ATTACHMENT
                            Filename to add as an attachment
