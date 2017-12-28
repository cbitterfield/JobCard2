'''
newmodule -- shortdesc

newmodule is a description

It defines classes_and_methods

@author:     Colin Bitterfield

@copyright:  2017 Edge Intereactive. All rights reserved.

@license:    license

@contact:    colin@bitterfield.com
@deffield    updated: 12/26/2017
'''
#===============================================================================
# Import 
#===============================================================================

import os
from string import Template
import logging
logger = logging.getLogger(__name__)

# Additional Libraries
from string import Template
import task
import subprocess





def produce(dest_vol, object, jobcard, config, volume, noexec):
    Error = False
    #===========================================================================
    # Programs needed
    #===========================================================================
    CONVERT=config['programs']['convert']
    MOGRIFY=config['programs']['mogrify']
                               
                               
    logger.debug("Destination Volume " + str(dest_vol))
    logger.debug("Object " + str(object))
    logger.debug("Jobcard " + str(jobcard))
    logger.debug("Config " + str(config))
    logger.debug("Volume " + str(volume))
    logger.debug("NoExec " + str(noexec))
    
        
    #===========================================================================
    # split object
    #===========================================================================
    
    try:
        object_name, object_number = object.split(".")
    except:
        object_name = object
        object_number = "0"
    
    #===========================================================================
    # Item Information for local use
    #===========================================================================
    logger.debug("Set item key value pairs")
    try:
        item_type = jobcard[object]['type'] if 'type' in jobcard[object] else None
        item_action = jobcard[object]['action'] if 'action' in jobcard[object] else None
        item_src = jobcard[object]['src'] if 'src' in jobcard[object] else None
        item_alignment = jobcard[object]['alignment'] if 'alignment' in jobcard[object] else None
        item_name = jobcard[object]['name'] if 'name' in jobcard[object] else None
        item_dir = jobcard[object]['dir'] if 'dir' in jobcard[object] else None
        item_thumbnail = jobcard[object]['thumbnail'] if 'thumbnail' in jobcard[object] else False
        item_watermark = jobcard[object]['watermark'] if 'watermark' in jobcard[object] else False
        item_suffix = jobcard[object]['suffix'] + str(object_number) if 'suffix' in jobcard[object] else "_" + str(object_number)
        item_ext = jobcard[object]['ext'] if 'ext' in jobcard[object] else None
        item_width = jobcard[object]['set_width'] if 'set_width' in jobcard[object] else None
        item_height = jobcard[object]['set_height'] if 'set_height' in jobcard[object] else None
        item_kbps = jobcard[object]['set_kbps'] if 'set_kbps' in jobcard[object] else None
        
        
    except Exception as e: 
        logger.error("Item values are not properly set, please correct error " + str(e))
        Error = True
    #===========================================================================
    # Get minimal clip Information needed for watermarking
    #===========================================================================
    try:    
    # Get Clip Information 
        clip_shorttitle = jobcard['clipinfo']['shorttitle']
        clip_title = jobcard['clipinfo']['title']
        clip_keywords = jobcard['clipinfo']['keywords']
        clip_star_name = jobcard['clipinfo']['star']['name'] if "name" in jobcard['clipinfo']['star'] else ''          
        clip_star2 = True if "star2" in jobcard['clipinfo'] else False
        if clip_star2:
            logger.info("Loading Star 2")
            clip_star2_name = jobcard['clipinfo']['star2']['name'] if "name" in jobcard['clipinfo']['star2'] else ''
        clip_supporting_name = jobcard['clipinfo']['supporting']['name'] if "name" in jobcard['clipinfo']['supporting'] else ''
        
              
        
    except Exception as e:  
        logger.warning("Not all clip variables set properly; exception " + str(e)) 
        Error = True            
    
    
    
    
    
    #===========================================================================
    # Setup Module Destination Locations
    #===========================================================================
    output = config['default'][dest_vol]
    projectno = jobcard['clipinfo']['projectno']
    edgeid = jobcard['clipinfo']['edgeid']
    prime_dubya = jobcard['clipinfo']['prime_dubya']
    destination = output + "/" + projectno + "/" + prime_dubya + "/" + edgeid
    
    
    #setup final destination in complex situations
    logger.debug("Destination: " + str(destination) + " Name: " + str(item_name) + " Dir: " + str(item_dir))
    if not item_name == None and not item_dir == None:
        finaldestination = destination + "/" + str(item_name) + "/" + str(item_dir)
    elif not item_name == None and item_dir == None:
        finaldestination = destination + "/" + str(item_name)
    elif item_name == None and not item_dir == None:
        finaldestination = destination + "/" + str(item_dir)     
    else:
        finaldestination = destination
    
    source_path = item_src.split("/")
    source = config['default']['mount'] + "/" + volume[source_path[0]]
    
    
    # setup source either absoulte or relative
    if item_src[0] != "/":                       
        logger.debug("Relative Path")
        item_source = source +   "/" + item_src
        
    else:
        logger.debug("Absolute Path")
        item_source = item_src  
    
    #===========================================================================
    # Make Directory if needed
    #===========================================================================
    
    if not os.path.isdir(finaldestination) and not noexec:
        logger.debug("Creating Directory for Destination " + str(finaldestination))
        os.makedirs(finaldestination)
    else:
        logger.debug("Directory will not be created")
    
    logger.info("Module starting for action produce")
    logger.info("Destination Volume " + str(dest_vol))
    logger.info("Destination Directory " + str(config['default'][dest_vol]))
    logger.info("Final Destination Directory " + str(finaldestination))
    logger.info("Source: " + str(item_source))
    logger.info("Suffix: " + str(item_suffix))
    logger.info("Extension:" + str(item_ext))
    
  
    #===========================================================================
    # Module variables
    #===========================================================================
    FileList = []

    #===========================================================================
    # Produce new images as needed
    #===========================================================================
    
    #===========================================================================
    # Make a list of files to work from
    # Validate Source even exists
    #===========================================================================
    
    if os.path.exists(item_source):
        pathName = os.path.dirname(item_source)
        if os.path.isfile(item_source):
            IsFile = True
            logger.debug("Source is a File")
            
        else:
            IsFile = False
                
                
            
    else:
        Error = True
        logger.error("Source " + str(item_source) + " does not exist")
        return Error
    
    if IsFile:
        FileList.append(item_source)
            
            
    else:
        logger.debug("Source is a directory " + str(item_source))
        for eachfile in os.listdir(item_source):
            if (not eachfile.startswith(".")) and (os.path.isfile(str(item_source) + "/" + str(eachfile))):
                FileList.append(str(item_source) + "/" + str(eachfile))
            else:
                logger.debug("ignoring " + str(eachfile))

    logger.debug(FileList)
    logger.debug(pathName)
    
    counter = 0
    
    
    for copyFile in FileList:
        fileCount = str( "%03d" % counter)
        if copyFile.endswith(".jpg") or copyFile.endswith(".jpeg") or copyFile.endswith(".tiff") or copyFile.endswith(".tiff") or copyFile.endswith(".png") or copyFile.endswith(".gif") or copyFile.endswith(".pdf"):
            newName = str(edgeid) + str(item_suffix) + "_" + fileCount + str(item_ext)
            logger.info("Process file: " + str(fileCount) + " - "+ str(copyFile) + " =>" + str(finaldestination) + " <= " + str(newName)) 
            if not item_height == None or not item_width == None:
                logger.debug("Resize Image")
                RESIZE = str(item_width) if not item_width == None else " "
                RESIZE = str(RESIZE) + "x" + str(item_height)  if not item_height == None else str(RESIZE) + "x"
                logger.debug("Resize to " + str(RESIZE))
                CMD = CONVERT + " -resize " + str(RESIZE) + " '" + str(copyFile) + "' '" + finaldestination + "/" +str(newName) + "'"
                logger.debug("Command: " + str(CMD)) 
                if not noexec:          
                    CMD_result = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)     
                    stdoutdata, stderrdata = CMD_result.communicate()
                    CMD_status = CMD_result.returncode
                    if CMD_status == 0:
                        logger.info("Conversion successful")
                        logger.debug(stdoutdata)
                    else:
                        logger.error("Conversion failed "+ str(CMD_status) + " " + str(stderrdata))
            else:
                logger.debug("Don't resize Image")
                
            counter = counter + 1
            
    #===========================================================================
    # make thumbnails if needed
    #===========================================================================
    pattern = "*" + item_suffix + "*"

    if item_thumbnail:
        Error = task.thumbnail(config,jobcard,finaldestination,pattern,noexec)
            
        
    
    #===========================================================================
    # create watermark images if needed
    #===========================================================================
    watermark_data = {}
    pattern = item_suffix
    if item_watermark:
        watermark_data['STAR'] = clip_star_name
        watermark_data['STAR2'] = clip_star2_name if clip_star2 else ""    
        watermark_data['SHORTTITLE'] = clip_shorttitle
        
        task.watermark(config, jobcard, finaldestination, watermark_data, pattern, noexec)
            
            
    logger.info("Module ending for action produce")
    logger.debug("Error " + str(Error))
    return(Error)


def exists(dest_vol,object, jobcard, config, volume, noexec):
    Error = False
    
    logger.debug("Destination Volume " + str(dest_vol))
    logger.debug("Object " + str(object))
    logger.debug("Jobcard " + str(jobcard))
    logger.debug("Config " + str(config))
    logger.debug("Volume " + str(volume))
    logger.debug("NoExec " + str(noexec))
    
        
    #===========================================================================
    # split object
    #===========================================================================
    
    try:
        object_name, object_number = object.split(".")
    except:
        object_name = object
        object_number = "0"
    
    #===========================================================================
    # Item Information for local use
    #===========================================================================
    logger.debug("Set item key value pairs")
    try:
        item_type = jobcard[object]['type'] if 'type' in jobcard[object] else None
        item_action = jobcard[object]['action'] if 'action' in jobcard[object] else None
        item_src = jobcard[object]['src'] if 'src' in jobcard[object] else None
        item_alignment = jobcard[object]['alignment'] if 'alignment' in jobcard[object] else None
        item_name = jobcard[object]['name'] if 'name' in jobcard[object] else None
        item_dir = jobcard[object]['dir'] if 'dir' in jobcard[object] else None
        item_thumbnail = jobcard[object]['thumbnail'] if 'thumbnail' in jobcard[object] else False
        item_watermark = jobcard[object]['watermark'] if 'watermark' in jobcard[object] else False
        item_suffix = jobcard[object]['suffix'] + str(object_number) if 'suffix' in jobcard[object] else "_" + str(object_number)
        item_ext = jobcard[object]['ext'] if 'ext' in jobcard[object] else None
        item_width = jobcard[object]['set_width'] if 'set_width' in jobcard[object] else None
        item_height = jobcard[object]['set_height'] if 'set_height' in jobcard[object] else None
        item_kbps = jobcard[object]['set_kbps'] if 'set_kbps' in jobcard[object] else None
        
        
    except Exception as e: 
        logger.error("Item values are not properly set, please correct error " + str(e))
        Error = True
        
    
    #===========================================================================
    # Get minimal clip Information needed for watermarking
    #===========================================================================
    try:    
    # Get Clip Information 
        clip_shorttitle = jobcard['clipinfo']['shorttitle']
        clip_title = jobcard['clipinfo']['title']
        clip_keywords = jobcard['clipinfo']['keywords']
        clip_star_name = jobcard['clipinfo']['star']['name'] if "name" in jobcard['clipinfo']['star'] else ''          
        clip_star2 = True if "star2" in jobcard['clipinfo'] else False
        if clip_star2:
            logger.info("Loading Star 2")
            clip_star2_name = jobcard['clipinfo']['star2']['name'] if "name" in jobcard['clipinfo']['star2'] else ''
        clip_supporting_name = jobcard['clipinfo']['supporting']['name'] if "name" in jobcard['clipinfo']['supporting'] else ''
        
              
        
    except Exception as e:  
        logger.warning("Not all clip variables set properly; exception " + str(e)) 
        Error = True            
        
    
    
    
    #===========================================================================
    # Setup Module Destination Locations
    #===========================================================================
    output = config['default'][dest_vol]
    projectno = jobcard['clipinfo']['projectno']
    edgeid = jobcard['clipinfo']['edgeid']
    prime_dubya = jobcard['clipinfo']['prime_dubya']
    destination = output + "/" + projectno + "/" + prime_dubya + "/" + edgeid
    
    
    #setup final destination in complex situations
    if not item_name == None and not item_dir == None:
        finaldestination = destination + "/" + str(item_name) + "/" + str(item_dir)
    elif not item_name == None and item_dir == None:
        finaldestination = destination + "/" + str(item_name)
    elif item_name == None and not item_dir == None:
        finaldestination = destination + "/" + str(item_dir)     
    else:
        finaldestination = destination
    
    source_path = item_src.split("/")
    source = config['default']['mount'] + "/" + volume[source_path[0]]
    
    
    # setup source either absoulte or relative
    if item_src[0] != "/":                       
        logger.debug("Relative Path")
        item_source = source +   "/" + item_src
        
    else:
        logger.debug("Absolute Path")
        item_source = item_src  
    
    #===========================================================================
    # Make Directory if needed
    #===========================================================================
    
    if not os.path.isdir(finaldestination) and not noexec:
        logger.debug("Creating Directory for Destination " + str(finaldestination))
        os.makedirs(finaldestination)
    else:
        logger.debug("Directory will not be created")
    
    logger.info("Module starting for action produce")
    logger.info("Destination Volume " + str(dest_vol))
    logger.info("Destination Directory " + str(config['default'][dest_vol]))
    logger.info("Final Destination Directory " + str(finaldestination))
    logger.info("Source: " + str(item_source))
    logger.info("Suffix: " + str(item_suffix))
    logger.info("Extension:" + str(item_ext))
    
    
    task.copyconvert(item_source, finaldestination, edgeid, item_ext, item_suffix, False, config, noexec)

    #===========================================================================
    # make thumbnails if needed
    #===========================================================================
    pattern = "*" + item_suffix + "*"

    if item_thumbnail:
        Error = task.thumbnail(config,jobcard,finaldestination,pattern,noexec)
            
        
    
    #===========================================================================
    # create watermark images if needed
    #===========================================================================
    watermark_data = {}
    pattern = item_suffix
    if item_watermark:
        watermark_data['STAR'] = clip_star_name
        watermark_data['STAR2'] = clip_star2_name if clip_star2 else ""    
        watermark_data['SHORTTITLE'] = clip_shorttitle
        
        task.watermark(config, jobcard, finaldestination, watermark_data, pattern, noexec)
            
            
    logger.info("Module ending for action produce")
    logger.debug("Error " + str(Error))
    return(Error)    
    
    
    
    logger.info("End exists action")
    return(Error)



def ignore(dest_vol,component, jobcard, config, volume, noexec):
    Error = False
    logger.warn("Ignoring action " + str(component))
    return(Error)