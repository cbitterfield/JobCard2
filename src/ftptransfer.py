#!/opt/local/bin/python
'''
Created on Dec 7, 2017

@author: colin
'''

import os
import ftplib 


sizeWritten = 0


def callback(block):
    global sizeWritten
    print sizeWritten
    sizeWritten += 8192
    print "size written " + str(sizeWritten)
    return


username = "Edgeinter11"   
password = "PornStars1" 
filename = "/edge/Scratch/Test01/GMCZ_Scenes/GMCZ0022/clips4sale/clips/GMCZ0022_1920x1080x6000_final.mp4"
host = "54.208.142.118"
destination = "clips"
basename = os.path.basename(filename)
print basename

if os.path.isfile(filename): 
    print str(filename) + " file exists"
    filehandle = open(filename,'rb')
    
try:
    ftp = ftplib.FTP(host,username,password)
    print ftp.getwelcome()

    ftp.set_pasv(True)   
    ftp.cwd(destination)
    print ftp.pwd()
    try:
        ftp.size(basename)
        print "File Exists"
    except:
        print "Uploadling new file"
        
    print ftp.storbinary('STOR ' + str(basename), filehandle, 8192, callback)


except Exception as e: 
        Error = True
        print("An error occured " + str(e))
              


    


    