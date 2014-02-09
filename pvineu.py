#!/usr/local/bin/python3.3
import requests
import difflib
import io
import smtplib
import json

with io.open('config.json', 'r', encoding='utf-8') as f:
	config = json.load(f)

s = requests.session()
loginparams = {'__ac_name': config['pviuser'], '__ac_password': config['pvipassword'], 'form.submitted': '1'}
s.post('https://pvineu.ifi.lmu.de/login_form', params = loginparams, headers = {'Content-Type': 'application/x-www-form-urlencoded'}, verify = False)
r = s.get('https://pvineu.ifi.lmu.de/download?filename=pruefungen.xml', verify = False, stream = True)

pruefxml = []
for line in r.iter_lines():
	if line:
		pruefxml.append("%s\n" % line.decode('utf-8'))

xmlfile = []
with io.open('pruefungen.xml', 'r', encoding='utf-8') as f:
	for line in f.readlines():
		xmlfile.append(line)
textdiff = []
for line in difflib.context_diff(xmlfile, pruefxml, fromfile='ALT', tofile='NEU'):
	textdiff.append(line)
if len(textdiff) > 0:
	htmldiff = difflib.HtmlDiff().make_file(xmlfile, pruefxml, fromdesc='ALT', todesc='NEU')

	message = """From: From PVIneu-Robot <%s>
To: <%s>
MIME-Version: 1.0
Content-type: text/html
Subject: PVIneu Changement-Notification

""" % (config['sender'], config['receiver'])

	for i in htmldiff:
		message += i
	
	message = message.encode('latin-1')

	try:
		smtpObj = smtplib.SMTP_SSL(config['smtpserver'])
		smtpObj.set_debuglevel(config['smtpdebuglevel'])
		smtpObj.login(config['smtpuser'], config['smtppassword'])
		smtpObj.sendmail(config['sender'], [config['receiver']], message)
		print("Successfully sent email")
	except smtplib.SMTPException:
		print("Error: unable to send email")

	with io.open('pruefungen.xml', 'w', encoding='utf-8') as f:
		for line in pruefxml:
			f.write(line)

