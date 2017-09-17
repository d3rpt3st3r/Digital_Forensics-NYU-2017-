print('''\033[1m 
                                              $$$$$$$$$$$ THIS PROGRAM WAS CODED BY: $$$$$$$$$$$
                                                ___                                        ___
                                             __|||||__    NAME: ABHISHEK RAMCHANDRAN    __|||||__ 
                                               -+ +-  	     REG NUM: N15073991           -+ +- 
                                               --|--		NETID: ar4996             --|--
                                               -[~]-        HANDLE: aramchandran          -[~]-
------------------------------------------------------------------------------------------------------------------------------------------------
                                                             FILE CARVING RESULTS                     
------------------------------------------------------------------------------------------------------------------------------------------------
\033[0m''')
import binascii
import subprocess
#Extract the file names using list
output = subprocess.check_output("ls", shell=False)
output = output.split()

#List Definition
file_name = ["FILE NAME"]
magic_number = ["MAGIC NUMBER"]
md5hash_before = ["MD5 HASH BEFORE"]
md5hash_after = ["MD5 HASH AFTER"]
file_type = ["FILE TYPE"]
random_string = ["RANDOM STRING PRESENT?"]

#File-Type Dictionary Definition
a = open("a.txt","r")
d = dict()
for o in a:
    o = o.split()
    d[o[1]]=o[0]
a.close()

for i in output:
    if str(i,'ascii') == "document_reader.py" or str(i,'ascii')=="" or str(i,'ascii')=="a.txt":
        continue
    else:
        #Before Open, Find Hash
        query="md5sum "+str(i,'ascii')
        n = subprocess.check_output(query, shell=True)
        n = n.split()
        md5hash_before.append(str(n[0],'ascii'))
        #Open File
        f = open(i,"rb")
        a=f.read()[:4]
        file_name.append(str(i,'ascii'))
        magic_number.append(str(binascii.hexlify(a),'ascii'))
        #Find File Type from Dictionary
        if (str(binascii.hexlify(a),'ascii').upper()) in d.keys():
            file_type.append(d[str(binascii.hexlify(a),'ascii').upper()])
            random_string.append("NO")
            f.close()
        else:
            f = open(i,"rb")
            a = f.read()
            if(len(a)<50 and str.isalnum(str(a,'ascii'))):
                file_type.append("ascii text")
                random_string.append("YES")
            else:
                file_type.append("")
                random_string.append("NO")
            f.close()
        #After Open, Find Hash
        n = subprocess.check_output(query, shell=True)
        n = n.split()
        md5hash_after.append(str(n[0],'ascii'))

#Beautiful Output
for u,v,w,x,y,z in zip(file_name, file_type, magic_number, random_string, md5hash_before, md5hash_after):
    print ('{:^16} {:^50} {:^16} {:^25} {:^40} {:^40}'.format(u,v,w,x,y,z))
