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
    # Get Star Information
    #===========================================================================
    try:
        clip_star_name = jobcard['clipinfo']['star']['name'] if "name" in jobcard['clipinfo']['star'] else ''
        
    except Exception as e: 
        logger.error("Clip values are not properly set, please correct error " + str(e))
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
    
    #===========================================================================
    # Get Thumbnail info (if requested)
    #===========================================================================

    if item_thumbnail:
        try:
            thumbnail_width = jobcard['thumbnails']['set_width'] if 'set_width' in jobcard['thumbnails'] else 96
            thumbnail_height = jobcard['thumbnails']['set_height'] if 'set_height' in jobcard['thumbnails'] else 96
            thumbnail_dir = jobcard['thumbnails']['dir']  if 'dir' in jobcard['thumbnails'] else "thumbs"
            thumbnail_suffix = jobcard['thumbnails']['suffix']  if 'suffix' in jobcard['thumbnails'] else "_T"
            thumbnail_ext = jobcard['thumbnails']['ext']  if 'ext' in jobcard['thumbnails'] else ".jpg"
            thumbnail_size = str(thumbnail_width) + "x" + str(thumbnail_height)
            thumbnail_destination = finaldestination + "/" + thumbnail_dir
            
        
        except Exception as e: 
            logger.error("Thumbnail values are not properly set, please correct error " + str(e))
            Error = True    

    #===========================================================================
    # Get Watermark Info (If requested)
    #===========================================================================

    if item_watermark:
        try:
            watermark_dir = jobcard['watermark']['dir']  if 'dir' in jobcard['watermark'] else "watermark"
            watermark_suffix = jobcard['watermark']['suffix']  if 'suffix' in jobcard['watermark'] else "_W"
            watermark_ext = jobcard['watermark']['ext']  if 'ext' in jobcard['watermark'] else ".jpg"
            watermark_template = jobcard['watermark']['template']  if 'template' in jobcard['watermark'] else ""
            watermark_fontsize = jobcard['watermark']['fontsize']  if 'fontsize' in jobcard['watermark'] else 100
            watermark_color = jobcard['watermark']['color']  if 'color' in jobcard['watermark'] else "purple"
            watermark_videofontsize  = jobcard['watermark']['videofontsize']  if 'videofontsize' in jobcard['watermark'] else 30
            watermark_font = config['watermark']['font']  if 'font' in config['watermark'] else ""
            watermark_copysymbol = config['watermark']['copysymbol']  if 'copysymbol' in config['watermark'] else "(c)"
            watermark_location = jobcard['watermark']['location']  if 'location' in jobcard['watermark'] else "southeast"
            watermark_destination = finaldestination + "/" + watermark_dir
        
        except Exception as e: 
            logger.error("Watermark values are not properly set, please correct error " + str(e))
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
        
    if not os.path.isdir(watermark_destination) and not noexec and item_watermark:
        logger.debug("Creating watermark directory destination " + str(watermark_destination))
        os.makedirs(watermark_destination)
    else:
        logger.debug("watermark directory will not be created")
    
    if not os.path.isdir(thumbnail_destination) and not noexec and item_thumbnail:
        logger.debug("Creating thumbnail directory destination " + str(thumbnail_destination))
        os.makedirs(thumbnail_destination)
    else:
        logger.debug("thumbnail directory will not be created")
        
    
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

    if item_thumbnail:

        CMD_TEMPLATE = "$MOGRIFY -resize $SIZE -background white -gravity center -extent $SIZE -format jpg -quality 75 -path $THUMBDIR ${CAPTURE}/*${EXT}"            
        CMD = Template(CMD_TEMPLATE).safe_substitute(MOGRIFY=MOGRIFY, SIZE=thumbnail_size, THUMBDIR=thumbnail_destination, CAPTURE=finaldestination, EXT=thumbnail_ext)
        logger.debug("Thumbnail Command: " + CMD)
        
        command = {}
        command_status = {}
        command_name = 'thumbnail'
    
        # Run Command
        
        if noexec:
            command[command_name] = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            logger.warning("Running Command - " + str(command_name))  
            command[command_name] = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
            logger.info( "COMMAND" + command_name + " for "+ item_src + " Started" )
            
        
    
    #===========================================================================
    # create watermark images if needed
    #===========================================================================
    
    
     
    watermark_text = Template(watermark_template).safe_substitute(STAR=clip_star_name, COPYRIGHT=watermark_copysymbol.encode('utf-8'))
    for markFile in os.listdir(finaldestination):
        if os.path.isfile(str(finaldestination) + "/" + str(markFile)):
            fileBase, fileExt = markFile.split('.')
            CMD_TEMPLATE = "$CONVERT '${FINALDESTINATION}/${MARKFILE}'  -background none -font $FONT -fill $COLOR -gravity $LOCATION -pointsize $FONTSIZE -annotate 0 '$TEXT' -flatten '${WATERDESTINATION}/${ORIGFILE}${SUFFIX}${EXT}'" 
            CMD = Template(CMD_TEMPLATE).safe_substitute(CONVERT=CONVERT, MARKFILE=markFile, COLOR=watermark_color, FINALDESTINATION=finaldestination, FONT=watermark_font, LOCATION=watermark_location, FONTSIZE=watermark_fontsize, EXT=watermark_ext , SUFFIX=watermark_suffix, TEXT=watermark_text, ORIGFILE=fileBase, WATERDESTINATION=watermark_destination)
            
            if not noexec:
                command[fileBase] = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info("Watermark Command " + str(CMD))
       
        
    #===========================================================================
    # Verify all subprocesses have completed.
    #===========================================================================
    if not noexec:
        # Check if Command executed
        
        for eachProcess in command:
            logger.info("Check if " + str(eachProcess) + " Completed")
            stdoutdata, stderrdata = command[eachProcess].communicate()
            command_status[eachProcess] = command[eachProcess].returncode 
            if command_status[eachProcess] == 0:
                logger.info(str(eachProcess) + " Completed, returned Status: " + str(command_status[eachProcess]))
                logger.debug(stdoutdata)
            else:
                logger.error(str(eachProcess) + "failed, with Status:"+ str(command_status[eachProcess]))
                logger.error(stderrdata)
                Error = True

        

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