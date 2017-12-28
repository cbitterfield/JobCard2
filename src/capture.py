#-*- coding: utf-8 -*-
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
import subprocess
import task





def produce(dest_vol, object, jobcard, config, volume, noexec):
    #===============================================================================
    # Define Needed Programs
    #===============================================================================
    CONVERT=config['programs']['convert']
    FFMPEG=config['programs']['ffmpeg']
    FFPROBE=config['programs']['ffprobe']
    MOGRIFY=config['programs']['mogrify']
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
        item_frame_every =  jobcard[object]['frame_every'] if 'frame_every' in jobcard[object] else 30
        
        
        
    except Exception as e: 
        logger.error("Item values are not properly set, please correct error " + str(e))
        Error = True
        
    #===========================================================================
    # Setup Module Destination Locations
    #===========================================================================
    output = config['default'][dest_vol]
    projectno = jobcard['clipinfo']['projectno']
    edgeid = jobcard['clipinfo']['edgeid']
    prime_dubya = jobcard['clipinfo']['prime_dubya']
    destination = output + "/" + projectno + "/" + prime_dubya + "/" + edgeid
    
    
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
    
    #setup final destination in complex situations
    if not item_name == None and not item_dir == None:
        finaldestination = destination + "/" + str(item_name) + "/" + str(item_dir)
    elif not item_name == None and item_dir == None:
        finaldestination = destination + "/" + str(item_name)
    elif item_name == None and not item_dir == None:
        finaldestination = destination + "/" + str(item_dir)     
    else:
        finaldestination = destination
        
    #===========================================================================
    # Get Codec Information
    #===========================================================================
    try:
        mp4_decode = config['codec']['mp4_decode'] if "mp4_decode" in config['codec'] else "h264"
        mp4_encode = config['codec']['mp4_encode'] if "mp4_encode" in config['codec'] else "h264"
        mp4_simple = config['codec']['mp4_simple'] if "mp4_simple" in config['codec'] else "mpeg4"
        mp4_jpeg = config['codec']['mp4_jpeg'] if "mp4_jpeg" in config['codec'] else "mjpeg"
        mp4_accel = config['codec']['mp4_accel'] if "mp4_accel" in config['codec'] else '-hwaccel videotoolbox'
        mp4_threads = config['codec']['mp4_threads'] if "mp4_threads" in config['codec'] else "-threads 8"
        mp4_scalefilter = config['codec']['mp4_scalefilter'] if "mp4_scalefilter" in config['codec'] else "-scale"
        
        
    except Exception as e: 
        logger.error("Codec values are not properly set, please correct error " + str(e))
        Error = True
    
 
    
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
    logger.info("Frame Every " + str(item_frame_every))
    logger.debug("FFPROBE " + str(FFPROBE))
    
    #===========================================================================
    # Step 1 Capture video sequence
    #===========================================================================
    #===========================================================================
    # Create Command
    #===========================================================================

    CMD = FFMPEG + " -c:v " + mp4_decode + " -i '"  + item_source + "' -thread_type slice -hide_banner -vf fps=1/" + str(item_frame_every) + "  -c:v " + mp4_jpeg  + " '" + finaldestination + "/" +  edgeid  + str(item_suffix) + "_%03d.jpg'" 
    logger.debug("Command " + str(CMD)) 

    #===========================================================================
    # Process command
    #===========================================================================
    command = {}
    command_status = {}
    command_name = 'capture'

    # Run Command
    
    if noexec:
        command[command_name] = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logger.warning("Running Command - " + str(command_name))  
        command[command_name] = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
        logger.info( "COMMAND" + command_name + " for "+ item_src + " Started" )
        
    if not noexec:
        # Check if Command executed
        logger.info("Check if " + str(command_name) + " Completed")
        stdoutdata, stderrdata = command[command_name].communicate()
        command_status[command_name] = command[command_name].returncode 
        if command_status[command_name] == 0:
            logger.info(str(command_name) + " Completed, returned Status: " + str(command_status[command_name]))
            logger.debug(stdoutdata)
        else:
            logger.error(str(command_name) + "failed, with Status:"+ str(command_status[command_name]))
            logger.error(stderrdata)
            Error = True

    #===========================================================================
    # Step 2 Create Watermark and Thumbnails
    #===========================================================================
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


def exists(dest_vol,component, jobcard, config, volume, noexec):
    Error = True
    logger.info("Not a valid action")
    return(Error)



def ignore(dest_vol,component, jobcard, config, volume, noexec):
    Error = False
    logger.warn("Ignoring action " + str(component))
    return(Error)