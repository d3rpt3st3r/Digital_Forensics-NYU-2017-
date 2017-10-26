#NECESSARY LIBRARIES
import progressbar
import sys
import os
import subprocess
import requests
import urlparse
import time
import sqlite3
from lxml import etree
from pykml.parser import Schema
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX


def kmlfile_location_IP(host_name):#LOCATION GENERATOR VIA QUERY TO FREEGEOIP
	query="freegeoip.net/json/"+host_name
	a = subprocess.check_output(['GET',query])
	#DECIDED TO WRITE MY OWN JSON SIFTER
	a = a.replace("{","")
	a = a.replace("}","")
	a = a.replace("\"","")
	a = a.replace(","," ")
	a = a.split()
	l = len(a)
	lon = str(a[l-2])
	lat = str(a[l-3])
	lon = lon.split(":")
	lat = lat.split(":")
	longitude = lon[1]
	latitude = lat[1]
	return latitude,longitude

def carve_location_info(host_name):#LOCATION GENERATOR VIA QUERY TO FREEGEOIP
	query="freegeoip.net/json/"+host_name
	loc = ""	
	a = subprocess.check_output(['GET',query])
	#DECIDED TO WRITE MY OWN JSON SIFTER
	a = a.replace("{","")
	a = a.replace("}","")
	a = a.replace("\"","")
	a = a.split(",")
	for i in a[1:]:
		loc+=str(i)+"\n"
	return loc		

def get_whois_info(host_name):#WHOIS QUERY VIA COMMAND LINE ARGS
	a = ""
	try:
		a = subprocess.check_output(['whois','-H',host_name])
		a= a.split("\n")
		s = ""
		for q in a:
			s+=str(q)+"\n"
		return s
	except subprocess.CalledProcessError as e:
		a = e.output
		a= a.split("\n")
		s = ""
		for q in a:
			s+=str(q)+"\n"
		return s

def get_request_header(host_name):#SERVER FINGERPRINT VIA GET REQUEST TO THE HOST
	r = ""
	r = requests.get(host_name)
	header = r.headers
	return header

def get_dns_record(host_name):#DNS RECORD GENERATOR
	a = ""
	a = subprocess.check_output(['dig',host_name])
	a= a.split("\n")
	dns_record = []
	for i in a:
		if (i.startswith(";")):
			continue
		elif(len(i)>2):
			dns_record.append(i)
		else:
			continue
	return dns_record

def generate_text_report():#CREATE A REPORT.TXT
	#TIME KEEPER
	start = time.time()
	whois_time=0
	header_time=0
	dns_time=0
	location_time=0

	d = dict()
	f = open("urls.txt","r")#LIST OF URLS
	count = 0
	main_result=""#MASTER STRING THAT WRITES TO FILE
	#STATUS BAR
	bar = progressbar.ProgressBar(maxval=65, \
	    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()
	for i in f:
		o = urlparse.urlparse(i)
		o = o.netloc
		main_result+="\n----------------------------------------------------\n"		
		main_result+="INFORMATION FOR "+i
		main_result+="\n----------------------------------------------------\n\n"
		# WHOIS INFORMATION
		prop=0
		prop=time.time()		
		main_result+="WHOIS RECORD: \n"
		c_d = o.count(".")
		if(c_d>1):
			n = o.split(".",c_d-1)
			m = len(n)
			root_domain= str(n[m-1])
		else:
			root_domain = o
		if(root_domain in d):
			who = d[root_domain]
		else:
			who = get_whois_info(root_domain)
			if(who==""):
				who = get_whois_info(root_domain)
			d[root_domain] = who
		main_result+=who
		main_result+="\n----------------------------------------------------\n\n"
		whois_time+=(time.time()-prop)
		# DNS RECORD
		prop=0
		prop=time.time()
		main_result+="DNS RECORD: \n"
		rec = get_dns_record(o)
		for k in rec:
			main_result+=k+"\n"
		main_result+="\n----------------------------------------------------\n\n"
		dns_time+=(time.time()-prop)
		# HEADER FINGERPRINT
		prop=0
		prop=time.time()
		main_result+="FINGERPRINT INFORMATION CAPTURED: \n"
		finger_print = get_request_header(i)
		for x in finger_print:		
			main_result+=x+": "+finger_print[x]+"\n"
		main_result+="\n----------------------------------------------------\n\n"		
		header_time+=(time.time()-prop)
		# LOCATION INFORMATION
		prop=0
		prop=time.time()
		main_result+="LOCATION INFORMATION: \n"
		loc = carve_location_info(o)
		main_result+=loc
		main_result+="\nx-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x\n\n"
		location_time+=(time.time()-prop)
		count+=1

		#STATUS KEEPER
		bar.update(count)
	bar.finish()
	#REPORT WRITER
	f1 = open("report.txt","w")
	f1.write(main_result)
	f.close()
	f1.close()
	stop = time.time()
	#PROGRAM OUTPUT
	print("Report.txt generated successfully in "+str((stop-start)/60)+" mins.")
	print("TIME STATS")
	print("1.Average WHOIS TIME: "+str(((whois_time/65)/60))+" mins")
	print("2.Average DNS RECORD TIME: "+str(((dns_time/65)/60))+" mins")
	print("3.Average FINGERPRINT TIME: "+str(((header_time/65)/60))+" mins")
	print("4.Average LOCATION TIME: "+str(((location_time/65)/60))+" mins")

def generate_kml_output():
	start = time.time() #TIME KEEPER	
	d = dict()
	f= open("urls.txt","r")
	count = 0
	#STATUS BAR
	bar = progressbar.ProgressBar(maxval=65, \
	    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()
	
	for i in f:
		i = i.rstrip()
		o = urlparse.urlparse(i)
		o = o.netloc
		lat,lon = kmlfile_location_IP(o) #GET LOCATION INFO
		val = lon+","+lat
		d[o] = val
		count+=1
		#STATUS KEEPER
		bar.update(count)
	bar.finish()
	doc = KML.kml(KML.Document()) #CREATE DOC BASE FOR KML
	for a in d:
		place_marker = KML.Placemark(KML.name(a),KML.Point(KML.coordinates(d[a])))#CREATE PLACEMAKER AND POINT INKML
		doc.Document.append(place_marker)
	fp = open("report.kml","w")
	fp.write(etree.tostring(doc, pretty_print=True))#PARSE AS XML AND WRITE TO FILE
	fp.close()
	f.close()
	stop=time.time()
	#PROGRAM OUTPUT
	print("KML File was written successfully in "+str((stop-start)/60)+" mins. Check report.kml")

def generate_sqlite_db():
	#TIME KEEPER
	start = time.time()
	whois_time=0
	header_time=0
	dns_time=0
	location_time=0

	d = dict()
	f = open("urls.txt","r")
	count = 0
	#DB CALL AND CREATE
	db = sqlite3.connect("report.db")
	db.text_factory=str
	cur=db.cursor()
	cur.execute("DROP TABLE IF EXISTS report")
	cur.execute("CREATE TABLE IF NOT EXISTS report (Website BLOB, WHOIS_information BLOB, DNS_lookup_information BLOB, Server_Fingerprint BLOB, Location_Information BLOB)")
	
	t_w = 65
	#STATUS BAR
	bar = progressbar.ProgressBar(maxval=65, \
	    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()

	for i in f:
		main_result=list()		
		o = urlparse.urlparse(i)
		o = o.netloc
		dr=""
		poc=""
		fngr=""
		# WHOIS INFORMATION
		prop=0
		prop=time.time()
		c_d = o.count(".")
		if(c_d>1):
			n = o.split(".",c_d-1)
			m = len(n)
			root_domain= str(n[m-1])
		else:
			root_domain = o
		if(root_domain in d):
			who = d[root_domain]
		else:
			who = get_whois_info(root_domain)
			if(who==""):
				who = get_whois_info(root_domain)
			d[root_domain] = who
		whois_time+=(time.time()-prop)
		# DNS RECORD
		prop=0
		prop=time.time()
		rec = get_dns_record(o)
		for k in rec:
			dr+=k+"\n"
		dns_time+=(time.time()-prop)
		# HEADER FINGERPRINT
		prop=0
		prop=time.time()
		finger_print = get_request_header(i)
		for x in finger_print:		
			fngr+=x+": "+finger_print[x]+"\n"
		header_time+=(time.time()-prop)
		# LOCATION INFORMATION
		prop=0
		prop=time.time()
		poc = carve_location_info(o)
		location_time+=(time.time()-prop)

		#WRITE TO DB
		something=(i,who,dr,fngr,poc)
		cur.execute("""INSERT INTO report (Website, WHOIS_information, DNS_lookup_information, Server_Fingerprint, Location_Information) VALUES (?,?,?,?,?);""",something)
		db.commit()

		count+=1
		#STATUS KEEPER
		bar.update(count)
	bar.finish()
	f.close()
	stop = time.time()
	#PROGRAM OUTPUT
	print("Report.db generated successfully in "+str((stop-start)/60)+" mins.")
	print("TIME STATS")
	print("1.Average WHOIS TIME: "+str(((whois_time/65)/60))+" mins")
	print("2.Average DNS RECORD TIME: "+str(((dns_time/65)/60))+" mins")
	print("3.Average FINGERPRINT TIME: "+str(((header_time/65)/60))+" mins")
	print("4.Average LOCATION TIME: "+str(((location_time/65)/60))+" mins")

def main():#MAIN FUNCTION
	#FANCY PANEL FOR USER FRIENDLY-ISH CONSOLE
	print("Welcome to the ultimate Data Carver: ")
	print("What kind of information would you like?")
	print("1. Text File Report")
	print("2. SQLITE DB")
	print("3. KML File (Google Earth Plot)")
	choice = raw_input("Enter Your Choice: ")
	#CHOICE MASTER
	if(choice.isdigit()):
		if(int(choice) == 1):
			print("You will get a text report.")
			generate_text_report()
		elif(int(choice) == 2):
			print("You will get a SQL DB.")
			generate_sqlite_db()
		elif(int(choice) == 3):
			print("You will get a KML file.")
			generate_kml_output()

main()#ONE LINE THAT DECIDES THE FATE OF THIS PROGRAM...
