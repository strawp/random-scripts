#!/usr/bin/python
import argparse, subprocess, requests, shutil
import sys
import os.path

# Convert a Burp .der file to pem and install it on the connected Android device over ADB


pipes = []

parser = argparse.ArgumentParser(description="Download and convert a Burp CA cert to PEM format and install it on the ADB connected device")
parser.add_argument("-p", "--burpport", default=8080, help="Port number burp is running on")
parser.add_argument("-b", "--burphost", default='localhost', help="Host that burp is running on")
args = parser.parse_args()

print 'Installing the currently running Burp CA cert onto the currently connected Android device...'

# Download cert from Burp
# 
# curl -H "Host: burp" http://<Burp IP>:8080/cert -o cacert.der
print ''
print 'Downloading cert from Burp'
r = requests.get('http://' + args.burphost + ':' + str( args.burpport ) + '/cert', stream=True)
with open('cacert.der','wb') as f:
  shutil.copyfileobj(r.raw, f)

# Convert to pem
# 
# openssl x509 -inform der -in cacert.der -out burp.pem
print ''
print 'Converting to PEM'
subprocess.call('openssl x509 -inform der -in cacert.der -out burp.pem', shell=True)

# Generate the hash which will be become the cert name
# 
# openssl x509 -inform PEM -subject_hash_old -in burp.pem | head -1
print ''
print 'Getting hash'
certhash = subprocess.check_output('openssl x509 -inform PEM -subject_hash_old -in burp.pem | head -1', shell=True).strip()
print 'Hash: ' + certhash
certhash += '.0'

# Rename the burp.Pem to <hash>.0
# 
# mv burp.pem <hash>.0
print ''
print 'Renaming to ' + certhash
shutil.move( 'burp.pem', certhash)

# Adb push to the sdcard
# 
# adb push <hash>.0 /sdcard/Download
print ''
print 'Uploading to device'
subprocess.call('adb push ' + certhash + ' /sdcard/Download', shell=True )
subprocess.call("adb shell 'ls -l /sdcard/Download'", shell=True )

# Adb shell remount system partition as readwrite
# 
# adb shell
# su
# mount -o remount,rw /system
print ''
print 'Remounting system as writable'
subprocess.call("adb shell su root 'mount -o remount,rw /system'", shell=True )
subprocess.call("adb shell su root 'mount | grep system'", shell=True )

# Mv cert to the /system/etc/security/cacerts
# 
# mv /sdcard/Download/<hash>.0 /system/etc/security/cacerts
print ''
print 'Moving cert into system cacerts dir'
subprocess.call("adb shell su root 'mv /sdcard/Download/"+certhash+" /system/etc/security/cacerts'", shell=True )

# chmod 644 /system/etc/security/cacerts/<hash>.0
print ''
print 'Changing permissions to 644'
subprocess.call("adb shell su root 'chmod 644 /system/etc/security/cacerts/"+certhash+"'", shell=True )

# Adb shell remount system partition as read
# 
# mount -o remount,r /system
print ''
print 'Remounting as system as read only'
subprocess.call("adb shell su root 'mount -o remount,r /system'", shell=True )
