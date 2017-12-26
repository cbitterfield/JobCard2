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

def filetransfer(config, location, account, filename, path, noexec):
    logger.info("Starting filetransfer")
    Error = False
    
    # Assign Variables from Config
    try:
        ftpsite = config[location]['ftpsite'] if "ftpsite" in config[location] else None
        password = config[location][account] if account in config[location] else None
        basename = os.path.basename(filename)
        logger.info("FTP Site: " + str(ftpsite))
        logger.info("Account: " + str(account))
        logger.info("Password: " + str(password))
        filehandle = open(filename,'rb')
        if os.path.isfile(filename):
            logger.info("File " + str(basename) + " exists")
        else:
            Error = True
            logger.error("File " + str(basename) + " does not exists")
        
        # Open FTP Connection
        
        ftp = ftplib.FTP(ftpsite,account,password)
        logger.info(ftp.getwelcome())
        
        # Set Passive Mode
        ftp.set_pasv(True)   
        
        # Change to and check destination
        try:
            logger.info(ftp.cwd(path))
        except Exception as e:
            logger.error(ftplib.error_perm)
            logger.error("Can't change directory")
            logger.warn("An error occured " + str(e)) 
            Error = True
                
        logger.info("FTP Remote Directory: " + str(ftp.pwd()))
        
        if Error == False:
        
            try:
                ftp.size(basename)
                logger.info( str(basename) +  " File Exists, existing file will be overwritten")
            except:
                logger.info("Uploadling new file:" + str(basename))
            
            try:            
                ftp_message = ftp.storbinary('STOR ' + str(basename), filehandle, 8192)
                logger.info(ftp_message)
            except Exception as e:
                logger.warn("An error occured " + str(e)) 
                Error = True
        else:
            logger.error("Processing terminated, an error occurred")
            
        logger.info("Close FTP Connection")
        ftp.close()
        
    except Exception as e: 
        Error = True
        logger.warn("An error occured " + str(e))    
    
    
    
    return Error
 
def test(test_text):
    
    print "Test"
    
    return(test)   

def getmd5(config, filename, noexec):
    MD5=config['locations']['md5']
    value=subprocess.check_output([MD5, filename])
    myMD5,basename = value.split()
    logger.info("MD5: " + filename + " = " + myMD5)
    return myMD5


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

