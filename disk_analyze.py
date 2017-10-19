import sys
import os
import subprocess
import sqlite3
import exifread
from PyPDF2 import PdfFileReader
os.system("sudo mkdir Carved_Files")
os.system("sudo mkdir Carved_Files/useful_files")
db = sqlite3.connect("Carved_Files/File_Report.db")
useful_things = list()
#DATABASE CONNECTION AND ADDITION
def sq_db_add(useful_things):
	db.text_factory=str
	cur=db.cursor()
	cur.execute("DROP TABLE IF EXISTS report")
	cur.execute("CREATE TABLE IF NOT EXISTS report (filename BLOB, md5 BLOB, metadata NULLABLE BLOB)")
	for k in useful_things:
		something=(str(k[0]),str(k[1]),str(k[2]))
		cur.execute("""INSERT INTO report (filename, md5, metadata) VALUES (?,?,?);""",something)
		db.commit()
#CALL LOCAL DICT TO DD VALUES AND EXPORT REPORT
def call_database(fi,file_name):
	lop=[]
	fil_meta=""
	q1= subprocess.check_output("sudo md5sum Carved_Files/useful_files/"+file_name+"/"+fi, shell=True)
	q1=q1.split()
	q2= subprocess.check_output("sudo file -b Carved_Files/useful_files/"+file_name+"/"+fi, shell=True)
	if q2.startswith("PDF"):
		if("\\" in fi):		
			fi = fi.replace("\\","")
		fr=open("Carved_Files/useful_files/"+file_name+"/"+fi, "rb")
		try:		
			mets = PdfFileReader(fr)
			fil_meta=mets.getDocumentInfo()
			lop = [fi,q1[0],fil_meta]
		except:
			lop = [fi,q1[0],"None"]
			pass
	else:
		if("\\" in fi):		
			fi = fi.replace("\\","")		
		fr=open("Carved_Files/useful_files/"+file_name+"/"+fi, "rb")		
		fil_meta = exifread.process_file(fr, details=False)		
		lop = [fi,q1[0],fil_meta]
	useful_things.append(lop)
#STORE IMAGES AND PDFs
def useful_files(file_name):
	q = subprocess.check_output("sudo ls Carved_Files/"+file_name, shell=True)
	q=q.split("\n")
	q.remove("")	
	for i in d:	
		a = subprocess.check_output("sudo file -b Carved_Files/"+file_name+"/"+d[i], shell=True)
		if(a.startswith("JPEG") or a.startswith("PC bitmap") or a.startswith("PDF")):
			os.system("sudo cp Carved_Files/"+file_name+"/"+d[i]+" Carved_Files/useful_files/"+file_name+"/"+d[i])
			call_database(d[i],file_name,)
#PARSE FILE PATHS
def parse_filename(fil_name):
	fil_name=fil_name.split("/")
	fil=fil_name[len(fil_name)-1]
	return fil
#PARSE VISIBLE FILES	
def extract_visible_files(file_name):
	n = subprocess.check_output("sudo fls -u -F -r "+file_name, shell=True)
	n=n.split("\n")
	n.remove("")
	for i in n:		
		i=i.split(' ',1)
		tup = i[1].split('\t')
		if('.' in tup[1]):
			if '/' in tup[1]:
				tup[1]=parse_filename(tup[1])
			tup[1]=tup[1].replace(" ","\ ")	
			d[tup[0][:-1]]=tup[1]
		else:
			continue
	for i in d:
		os.system("sudo icat "+file_name+" "+i+" > Carved_Files/"+file_name+"/"+d[i])
	useful_files(file_name)
#PARSE DELETED FILESS	
def extract_deleted_files(file_name):
	n = subprocess.check_output("sudo fls -d -F -r "+file_name, shell=True)
	n=n.split("\n")
	n.remove("")
	for i in n:		
		i=i.split(' ',2)
		tup = i[2].split('\t')
		if('.' in tup[1]):
			if '/' in tup[1]:
				tup[1]=parse_filename(tup[1])
			tup[1]=tup[1].replace(" ","\ ")		
			d[tup[0][:-1]]=tup[1]
		else:
			continue
	for i in d:
		os.system("sudo icat "+file_name+" "+i+" > Carved_Files/"+file_name+"/"+d[i])
	useful_files(file_name)
#MAIN
for file_name in ["File1.163b3a010e0a50e264deb098c77daea7.001","File2.16c023257b0642f046e9a72ce7a2239a.001"]:
	d = dict()	
	os.system("sudo mkdir Carved_Files/"+file_name)
	os.system("sudo mkdir Carved_Files/useful_files/"+file_name)
	extract_visible_files(file_name)
	d = dict()
	extract_deleted_files(file_name)
	os.system("sudo rm -r Carved_Files/"+file_name)
a= open("Carved_Files/report.txt","w")
a.write("File_Name\tMD5\tMetadata\n")
for c in useful_things:
	a.write(c[0]+"\t"+c[1]+"\t"+str(c[2])+"\n")
a.close()
sq_db_add(useful_things)
db.close()
