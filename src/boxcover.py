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
    Error = False
    
    #===========================================================================
    # Setup Needed Programs
    #===========================================================================
    CONVERT=config['programs']['convert']
    
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
        item_width = jobcard[object]['set_width'] if 'set_width' in jobcard[object] else 3724
        item_height = jobcard[object]['set_height'] if 'set_height' in jobcard[object] else 5616
        item_kbps = jobcard[object]['set_kbps'] if 'set_kbps' in jobcard[object] else None
        
        
    except Exception as e: 
        logger.error("Item values are not properly set, please correct error " + str(e))
        Error = True
        
    #===========================================================================
    # Get Boxcover information from Config
    #===========================================================================
    
    try:
        boxcover_font = config[object]['font'] if "font" in config[object] else None
        boxcover_star_size = config[object]['star_size'] if "star_size" in config[object] else 150
        boxcover_edgeid_size = config[object]['edgeid_size'] if "edgeid_size" in config[object] else 50
        boxcover_support_size = config[object]['support_size'] if "support_size" in config[object] else 120
        boxcover_shortitle_size = config[object]['shorttitle_size'] if "shorttitle_size" in config[object] else 120
        boxcover_title_size = config[object]['title_size'] if "title_size" in config[object] else 160
        boxcover_title_location = config[object]['title_location'] if "title_location" in config[object] else "right"
        boxcover_font_color = config[object]['font_color'] if "font_color" in config[object] else "White"
        boxcover_back_suffix = config[object]['back_suffix'] if "back_suffix" in config[object] else "_back"
        boxcover_density = config[object]['density'] if "density" in config[object] else 72
  
    except Exception as e: 
        logger.error("Boxcover values are not properly set, please correct error " + str(e))
        Error = True
  
  
    
    #===========================================================================
    # Get Clip Info needed
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
    # Display Clip information if debug is on
    #===========================================================================
    
    logger.debug("Short Title: " + str(clip_shorttitle))
    logger.debug("Title: " + str(clip_title))
    logger.debug("Star Name: " + str(clip_star_name))
    if clip_star2:
        logger.debug("Star2 Name: " + str(clip_star2_name))
    logger.debug("Supporting: " + str(clip_supporting_name))
    logger.debug("Title Size " + str(boxcover_title_size))
    logger.debug("Short Title Size " + str(boxcover_shortitle_size))
    logger.debug("Star Size " + str(boxcover_star_size))
    logger.debug("Support Star Size " + str(boxcover_support_size))
    logger.debug("Font " + str(boxcover_font))
    logger.debug("Density " + str(boxcover_density))
    
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
    
    
    #===========================================================================
    # Display if Debug 
    #===========================================================================
    logger.debug("Module starting for action produce")
    logger.debug("Destination Volume " + str(dest_vol))
    logger.debug("Destination Directory " + str(config['default'][dest_vol]))
    logger.debug("Final Destination Directory " + str(finaldestination))
    logger.debug("Source: " + str(item_source))
    logger.debug("Suffix: " + str(item_suffix))
    logger.debug("Extension:" + str(item_ext))
    
   
    #===========================================================================
    # Start Creation
    #===========================================================================
    
    #===========================================================================
    # Clean up the title and short title for apostophes
    # Set up proper padding for Star and or Star2
    # Resize source image
    #===========================================================================
    
    boxcover_title = clip_title.replace("'","\\'")
    boxcover_shorttitle = clip_shorttitle.replace(" ","\\n")
    
    if item_alignment == 'left':
        boxcover_title = " " + boxcover_title
        if clip_star2:
            all_star = " " + clip_star_name + " & " + clip_star2_name
        else:
            all_star = " " + clip_star_name
        supporting = "  " + clip_supporting_name
        gravity='Northwest'
    if item_alignment == 'center':
        gravity = 'North'
        if clip_star2:
            all_star = clip_star_name + " & " + clip_star2_name
        else:
            all_star = clip_star_name
    if item_alignment == 'right':
        gravity='NorthEast'       
        boxcover_title = boxcover_title + " "
        if clip_star2:
            all_star = clip_star_name + " & " + clip_star2_name + " "
        else:
            all_star = clip_star_name + " "
        clip_supporting_name =  clip_supporting_name + "  "

    # Need to set resize to max edge
    max_size = max(item_height, item_width)
    if item_width == max_size:
        logger.debug("Image Landscape mode")
        resizeto = str(item_width) + "x"
    elif item_height == max_size:
        logger.debug("Image Portrait mode")
        resizeto = "x" + str(item_height)   
    
    # Make image the correct size or add black background if needed. 
    CMD_TEMPLATE = "$CONVERT -size ${WIDTH}x${HEIGHT} canvas:black '${ITEM_SOURCE}' -gravity ${GRAVITY} -resize $RESIZETO -density ${DENSITY} -crop ${WIDTH}x${HEIGHT} -flatten '${FINALDESTINATION}/${EDGEID}${SUFFIX}${BACK_SUFFIX}${EXT}'"
    CMD = Template(CMD_TEMPLATE).safe_substitute(CONVERT=CONVERT, ITEM_SOURCE=item_source, WIDTH=item_width, HEIGHT=item_height, GRAVITY=gravity, RESIZETO=resizeto, FINALDESTINATION=finaldestination, EDGEID=edgeid, SUFFIX=item_suffix, BACK_SUFFIX=boxcover_back_suffix, EXT=item_ext, DENSITY=boxcover_density)
    logger.debug("Resize Command: " + str(CMD))
    
    command = {}
    command_status = {}# 
    command_name = 'resize'
    
    # Run Command
    
    if noexec:
        command[command_name] = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logger.warning("Running Command - " + str(command_name))  
        command[command_name] = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
        logger.info( "COMMAND" + command_name + " for "+ item_src + " Started" )
        
    
    # Check if Command executed
    logger.info("Check if " + str(command_name) + " Completed")
    stdoutdata, stderrdata = command[command_name].communicate()
    command_status[command_name] = command[command_name].returncode 
    if command_status[command_name] == 0:
        logger.info(str(command_name) + " Completed, returned Status: " + str(command_status[command_name]))
    else:
        logger.error(str(command_name) + "failed, with Status:"+ str(command_status[command_name]))
        Error = True

    #===========================================================================
    # Debug Values
    #===========================================================================
    logger.debug("Title  " + str(boxcover_title) + " Size " + str(boxcover_title_size))
    logger.debug("Short Title " + str(boxcover_shorttitle) + " Size " + str(boxcover_shortitle_size))
    logger.debug("Star " + str(all_star) + " Size " + str(boxcover_star_size))
    logger.debug("Supporting " + str(clip_supporting_name) + " Size " + str(boxcover_support_size))

    #===========================================================================
    # Make Boxcover
    #===========================================================================
    RESIZE_IMG = "'" + finaldestination +  "/" + str(edgeid)  + str(item_suffix) + str(boxcover_back_suffix) + item_ext +"'"
    REMOVE_IMG = finaldestination +  "/" + str(edgeid)  + str(item_suffix) + str(boxcover_back_suffix) + item_ext
    BOX_PSD = "'"  + finaldestination +  "/" + str(edgeid)  + str(item_suffix) + ".psd'"
    BOX_IMG = "'" + finaldestination +  "/" + str(edgeid)  + str(item_suffix) + item_ext +"'"
    
    
    # Create Box Cover Command Template
    CMD_TEMPLATE = "$CONVERT -size ${WIDTH}x${HEIGHT} -label 'background' -background transparent xc:none -depth 8 -set colorspace:auto-grayscale off"
    CMD_TEMPLATE = CMD_TEMPLATE + "\( -label 'image' $IMAGENAME \) "
    CMD_TEMPLATE = CMD_TEMPLATE + 
    
    
    
    
    
    CMD = Template(CMD_TEMPLATE).safe_substitute(CONVERT=CONVERT, ITEM_SOURCE=item_source, WIDTH=item_width, HEIGHT=item_height, GRAVITY=gravity, RESIZETO=resizeto, FINALDESTINATION=finaldestination, EDGEID=edgeid, SUFFIX=item_suffix, BACK_SUFFIX=boxcover_back_suffix, EXT=item_ext, DENSITY=boxcover_density)                                             
    
    
    logger.debug("Box create command: " + str(CMD))

    # 
    command_name = 'createcover'
    
    # Run Command
    
    if noexec:
        command[command_name] = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logger.info("Running Command - " + str(command_name))  
        command[command_name] = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
        logger.info( "COMMAND " + command_name + " for "+ item_src + " Started" )
        # Check if Command executed
        logger.info("Check if " + str(command_name) + " Completed")
        stdoutdata, stderrdata = command[command_name].communicate()
        command_status[command_name] = command[command_name].returncode 
        if command_status[command_name] == 0:
            logger.info(str(command_name) + " Completed, returned Status: " + str(command_status[command_name]))
            logger.info("Removing tempfile " + str(RESIZE_IMG))
            os.remove(REMOVE_IMG)
        else:
            logger.error(str(command_name) + "failed, with Status:"+ str(command_status[command_name]))
            Error = True




    logger.info("Module ending for action produce")
    logger.debug("Error " + str(Error))
    return(Error)


def exists(dest_vol, object, jobcard, config, volume, noexec):
    Error = False
    
    #===========================================================================
    # Setup Needed Programs
    #===========================================================================
    CONVERT=config['programs']['convert']
    
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
    # Get Boxcover information from Config
    #===========================================================================
    
    try:
        boxcover_font = config[object]['font'] if "font" in config[object] else None
        boxcover_star_size = config[object]['star_size'] if "star_size" in config[object] else 150
        boxcover_edgeid_size = config[object]['edgeid_size'] if "edgeid_size" in config[object] else 50
        boxcover_support_size = config[object]['support_size'] if "support_size" in config[object] else 120
        boxcover_shortitle_size = config[object]['shorttitle_size'] if "shorttitle_size" in config[object] else 120
        boxcover_title_size = config[object]['title_size'] if "title_size" in config[object] else 160
        boxcover_title_location = config[object]['title_location'] if "title_location" in config[object] else "right"
        boxcover_font_color = config[object]['font_color'] if "font_color" in config[object] else "White"
        boxcover_back_suffix = config[object]['back_suffix'] if "back_suffix" in config[object] else "_back"
  
    except Exception as e: 
        logger.error("Boxcover values are not properly set, please correct error " + str(e))
        Error = True
  
  
    
    #===========================================================================
    # Get Clip Info needed
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
    # Display Clip information if debug is on
    #===========================================================================
    
    logger.debug("Short Title: " + str(clip_shorttitle))
    logger.debug("Title: " + str(clip_title))
    logger.debug("Star Name: " + str(clip_star_name))
    if clip_star2:
        logger.debug("Star2 Name: " + str(clip_star2_name))
    logger.debug("Supporting: " + str(clip_supporting_name))
    
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
    
    
    #===========================================================================
    # Display if Debug 
    #===========================================================================
    logger.debug("Module starting for action produce")
    logger.debug("Destination Volume " + str(dest_vol))
    logger.debug("Destination Directory " + str(config['default'][dest_vol]))
    logger.debug("Final Destination Directory " + str(finaldestination))
    logger.debug("Source: " + str(item_source))
    logger.debug("Suffix: " + str(item_suffix))
    logger.debug("Extension:" + str(item_ext))
    
    task.copyconvert(item_source, finaldestination, edgeid, item_ext, item_suffix, False, config, noexec)
    
    return(Error)



def ignore(dest_vol, object, jobcard, config, volume, noexec):
    Error = False
    logger.warn("Ignoring action " + str(object))
    return(Error)