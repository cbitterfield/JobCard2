#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
joblib -- shortdesc

joblib is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2017 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import shlex
from string import Template
import subprocess
import datetime
import logging
import ftplib
logger = logging.getLogger(__name__)

def videosize(source, config, noexec):
    # Get Video Information from a given file
    Error = False
    height = 1920
    width = 1020
    duration = '00:00:00'
    bkps = 1500

    FFMPEG=config['locations']['ffmpeg']
    FFPROBE=config['locations']['ffprobe']
    MD5=config['locations']['md5']
    
    CMD_TEMPLATE = "$FFPROBE  -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height,width,bit_rate,duration '$VIDEO'"
    CMD = Template(CMD_TEMPLATE).safe_substitute(FFPROBE=FFPROBE, VIDEO=source)
    
    pCMD = shlex.split(CMD)
    
    videoName = os.path.basename(source)
    pathName = os.path.dirname(source)
    
    logger.info("Get the Video Size Information for Video: " + videoName )
    logger.info("Source Dir:" + pathName )
    
    
    logger.info("Getting information about video: " + source)
    
    if noexec: 
        result=subprocess.check_output("echo")
        sizeofVideo="1920x1080"
        Duration="60"
        BitRate="1500000"
        myduration = '00:00:00'
        mybitrate = '1500'
    else:
        try:    
            result=subprocess.check_output(pCMD)
            cWidth = result.splitlines(True)[0]
            cHeight = result.splitlines(True)[1]
            cDuration = result.splitlines(True)[2]
            cBit_Rate = result.splitlines(True)[3]
            lWidth = cWidth.split("=")[1]
            lHeight = cHeight.split("=")[1]
            lDuration = cDuration.split("=")[1]
            lBitRate = cBit_Rate.split("=")[1]
            width = lWidth.replace('\n','')
            height = lHeight.replace('\n','')
            Duration = lDuration.replace('\n','')
            BitRate = lBitRate.replace('\n','')
            duration = Duration.replace('"','')
            BitRate = BitRate.replace('"','')
            sizeofVideo =  str(width) + "x" + str(height)
            myduration = str(datetime.timedelta(seconds=int(float(duration))))
            mybitrate = str(int(BitRate)/1000)  
        except Exception as e: 
            Error = True
            logger.warn("An error occured " + str(e))    
        
    logger.info("Video Source: Size: " + sizeofVideo + " Duration:" + myduration + " BitRate:" + mybitrate + " kbps" )
    
    # Return Height, Width, Duration,bitrate kbps and Error 
    return(Error, height, width, myduration, mybitrate)

def numimages(source, config, noexec):
    # Returns number of images jpeg and tif ONLY
    tif = 0
    jpg = 0
    
    if os.path.isdir(source) and not noexec:
        for filename in os.listdir(sourcedir):
            if filename.endswith(".tif"):
                tif = tif + 1
            if filename.endswith(".jpg"):
                jpg = jpg + 1
                
                 
            
            
    return(Error, jpg, tif)

def filetransfer(username, password, host, filename, destination):
    logger.info("Starting filetransfer")
    Error = False
    
    # Get basename of the file
    basename = os.path.basename(filename)
    
    #Verify file exists.
    if os.path.isfile(filename): 
        logger.info( str(filename) + " file exists" )
        filehandle = open(filename,'rb')
    else:
        Error = True
        logger.error( str(filename) + " file does not exists" )
        return Error
    

    # Connect with FTP Host
    logger.info("Connecting to " + str(host) + " as USER " + str(username))
    logger.info("Sending file: " + str(basename) + " to " + str(destination))
    logger.debug("using password " + str(password))
    try:
        ftp = ftplib.FTP(host,username,password)
        logger.debug( ftp.getwelcome() )

        ftp.set_pasv(True)   
        ftp.cwd(destination)
        logger.debug(ftp.pwd())
            
        try:
            ftp.size(basename)
            logger.warn( "File Exists: " + str(basename))
        except:
            logger.info("Uploadling new file " + str(basename))
                
        logger.info( ftp.storbinary('STOR ' + str(basename), filehandle, 8192) )
                
    except Exception as e: 
        Error = True
        logger.error("An error occured " + str(e))
        
    ftp.close()
    return Error
 
def test(test_text):
    
    print "Test"
    
    return(test)   

def md5(fname):
    import hashlib
    logger.info("Generating md5 for " + str(fname))
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def makeList (jobcard,object_eval):
    # Make an Array of Components and products
    logger.info("Evaluating Jobcard for Object type " + str(object_eval))
    myList = []
    for object in sorted(jobcard):
        object_type = jobcard[object]['type'] if "type" in jobcard[object] else None
        if object_type == object_eval:
            myList.append(object)
            
    return myList   



def validateitem(config, jobcard, volume, test_component):
    import importlib
    Error = False
    # Test for Module in config
    try:
        component, component_modifier = test_component.split(".")
        item_action = jobcard[test_component]["action"] if "action" in jobcard[test_component] else None
    except:
        component = test_component
        item_action = jobcard[test_component]["action"] if "action" in jobcard[test_component] else None
    logger.debug("Testing Component " + str(component))
    try:    
        module = config[component]['module'] if "module" in config[component] else None
    except Exception as e:
        logger.error("Problem with " + str(component) + " not registered in config")
        logger.error("Error " + str(e))
        Error = True
        module = None
        
    if item_action == 'produce' or item_action == 'exists':   
            
        if module == None:
            logger.error("Module for " + str(test_component) + " is missing")
            
        else:
            try:
                myModule = importlib.import_module(module)
            except Exception as e: 
                logger.error(str(e))
                logger.error(str(component) + " module " + str(module) + " failed to import check config file for correct module")
                Error = True
         
        #Test source
        try:
            item_src = jobcard[test_component]['src'] if "src" in jobcard[test_component] else None
        except:
            item_src = None
        
        if item_src == None:
            logger.error("Problem with " + str(test_component) + "No source file - this is a requirement")
            Error = True   
        else:   
            if item_src[0] != "/":
                logger.debug("Source - relative Path")
                path_list = item_src.split("/")
                item_source = config['default']['mount'] + "/" + volume[path_list[0]] + "/" + item_src
               
                
            else:
                logger.debug("Source - absolute Path")
                item_source = item_src
            
                        
            logger.info("Item " + str(test_component) + " source " + str(item_source))   
            if os.path.exists(item_source):
                logger.info(str(test_component) + " source exists " + str(item_source))
                if os.path.isfile(item_source):
                    logger.debug(str(test_component) + " source " + str(item_source) + " is a file")
                elif os.path.isdir(item_source):
                    logger.debug(str(test_component) + " source " + str(item_source) + " is a directory")
            else:
                logger.error(str(test_component) + " source " + str(item_source) + " does not exist")
                Error = True
    else:
        logger.info("Component " + str(test_component) + " is being ignored")     
            
    return Error

def copyconvert(source, destination, edgeid, ext, suffix, recursive, config, noexec):
    import os
    import subprocess
    import shutil

    Error = False
    
    # Setup program variables
    IDENTIFY = config['programs']['identify']
    CONVERT = config['programs']['convert']
    
    FileList = []
    
    #===========================================================================
    # Debug Values
    #===========================================================================
    logger.debug("Identify located " + str(IDENTIFY))
    logger.debug("Convert located " + str(CONVERT))
    logger.debug("Source: " + str(source))
    logger.debug("Destination: " + str(destination))
    logger.debug("Suffix: " + str(suffix))
    logger.debug("Extenstion: " + str(ext))
    logger.debug("Recursive: " + str(recursive))
    logger.debug("Noexec: " + str(noexec))


    #===========================================================================
    # Make a list of files to work from
    # Validate Source even exists
    #===========================================================================
    
    if os.path.exists(source):
        pathName = os.path.dirname(source)
        if os.path.isfile(source):
            IsFile = True
            
        else:
            IsFile = False
                
                
            
    else:
        Error = True
        logger.error("Source " + str(source) + " does not exist")
        return Error
    
    if IsFile:
        FileList.append(source)
            
            
    else:
        for eachfile in os.listdir(source):
            if (not eachfile.startswith(".")) and (os.path.isfile(str(source) + "/" + str(eachfile))):
                FileList.append(str(source) + "/" + str(eachfile))
            else:
                logger.debug("ignoring " + str(eachfile))

    logger.debug(FileList)
    logger.debug(pathName)
    
    #===========================================================================
    # Make Directory if needed
    #===========================================================================
    
    if not os.path.exists(destination) and not noexec:
        logger.debug("Creating Directory for Destination " + str(destination))
        os.makedirs(destination)
    else:
        logger.debug("Destination directory " + str(destination))
    
    #===========================================================================
    # What type of file are we dealing with
    # Deal with Image, Video, PDF or other types
    #===========================================================================
    
    
    #===========================================================================
    # Dealing with files that ImageMagick can deal with.
    #===========================================================================
    
    if (ext == '.jpg' ) or  (ext == '.jpeg' ) or (ext == '.tif' ) or (ext == '.tiff' ) or (ext == '.gif' ) or (ext == '.png' ) or (ext == '.pdf' ):
        logger.debug("image files")
        # Image files will convert to ext format. This includes PDFs
        for copyFile in FileList:
    
                
            if copyFile.endswith(".jpg") or copyFile.endswith(".jpeg") or copyFile.endswith(".tiff") or copyFile.endswith(".tiff") or copyFile.endswith(".png") or copyFile.endswith(".gif") or copyFile.endswith(".pdf"):
                baseName = os.path.basename(copyFile)
                Name, extName = baseName.split(".")
                # Check to see if destination file exsits.        
                newName = str(edgeid) + str(suffix) + str(ext)
                proposeName = str(destination) +"/" + str(newName)
                    
                if os.path.isfile(proposeName):            
                    newName = str(edgeid) + str(suffix) + "[" + str(baseName) + "]" + str(ext) 
                    logger.warn("Destination File exists, new name " + newName)
                else:
                    logger.info("New Name is " + str(newName))
                
                if ext == str('.' + extName):
                    logger.debug("simple copy for " + str(baseName))
                    try:
                        logger.debug("Copy " + copyFile  + " => " + destination + "/" + newName)
                        shutil.copy(copyFile, destination + "/" + newName)  if not noexec else logger.info("Noexec Flag")
                    except Exception as e: 
                        logger.error(e)
                        Error = True
                    
                else:
                    # Convert file from existing format to requested format
                    logger.debug("Convert File")
                    CMD = CONVERT + " '" + str(copyFile) + "' '" + destination + "/" +str(newName) + "'"
                    logger.debug("Command: " + str(CMD)) 
                    if not noexec:          
                        CMD_result = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)     
                        stdoutdata, stderrdata = CMD_result.communicate()
                        CMD_status = CMD_result.returncode
                    
        
            else:
                logger.warn("Improper file type detected, simple copy will occur")
                baseName = os.path.basename(copyFile)
                Name, extName = baseName.split(".")
                origExt = "." + extName
                # Check to see if destination file exsits.        
                newName = str(edgeid) + str(suffix) + str(origExt)
                proposeName = str(destination) +"/" + str(newName)
                
                if os.path.isfile(proposeName):            
                    newName = str(edgeid) + str(suffix) + "[" + str(baseName) + "]" + str(origExt) 
                    logger.warn("Destination File exists, new name " + newName)
                else:
                    logger.info("New Name is " + str(newName))
                try:
                    logger.debug("Copy " + copyFile  + " => " + destination + "/" + newName)
                    shutil.copy(copyFile, destination + "/" + newName)  if not noexec else logger.info("Noexec Flag")
                except Exception as e: 
                    logger.error(e)
                    Error = True
                
    else:
        # Everything else will be a simple copy.
        logger.debug("Non-Image files")
        for copyFile in FileList:
            baseName = os.path.basename(copyFile)
            Name, extName = baseName.split(".")
            origExt = "." + extName
            # Check to see if destination file exsits.        
            newName = str(edgeid) + str(suffix) +  str(origExt)
            proposeName = str(destination) +"/" + str(newName)
                    
            if os.path.isfile(proposeName):            
                newName = str(edgeid) + str(suffix) + "[" + str(baseName) + "]" + str(origExt) 
                logger.warn("Destination File exists, new name " + newName)
            else:
                logger.info("New Name is " + str(newName))
            try:
                logger.debug("Copy " + copyFile  + " => " + destination + "/" + newName)
                shutil.copy(copyFile, destination + "/" + newName)  if not noexec else logger.info("Noexec Flag")
            except Exception as e: 
                logger.error(e)
                Error = True    
            
    
    return Error