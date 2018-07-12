#!/usr/bin/env python3
#===============================================================================
SHORTDESC = "PROGRAM TO MAKE BOXCOVERS"

DESCRIPTION = """

It defines classes_and_methods
 
@author:     Colin Bitterfield
 
@copyright:  2017 Edge Intereactive. All rights reserved.
 
@license:    license

@contact:    colin@bitterfield.com
@deffield    updated: 07/12/2018
"""
#===============================================================================

#===============================================================================
# Set Global Variables
#===============================================================================
__all__ = []
__version__ = 0.1
__date__ = '2017-12-10'
__updated__ = '2018-07-12'

DEBUG = False
TEST = False
NOEXEC = False

#===============================================================================
# Import 
#===============================================================================

import os
import sys
from string import Template
import logging
logger = logging.getLogger(__name__)

# Additional Libraries
import subprocess
import task

# Import CLI parsing
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter





def produce(dest_vol, target, jobcard, config, volume, noexec):
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
        object_name, object_number = target.split(".")
    except:
        object_name = target
        object_number = "0"
    
    #===========================================================================
    # Item Information for local use
    #===========================================================================
    logger.debug("Set item key value pairs")
    try:
        item_type = jobcard[target]['type'] if 'type' in jobcard[target] else None
        item_action = jobcard[target]['action'] if 'action' in jobcard[target] else None
        item_src = jobcard[target]['src'] if 'src' in jobcard[target] else None
        item_alignment = jobcard[target]['alignment'] if 'alignment' in jobcard[target] else None
        item_name = jobcard[target]['name'] if 'name' in jobcard[target] else None
        item_dir = jobcard[target]['dir'] if 'dir' in jobcard[target] else None
        item_thumbnail = jobcard[target]['thumbnail'] if 'thumbnail' in jobcard[target] else False
        item_watermark = jobcard[target]['watermark'] if 'watermark' in jobcard[target] else False
        item_suffix = jobcard[target]['suffix'] + str(object_number) if 'suffix' in jobcard[target] else "_" + str(object_number)
        item_ext = jobcard[target]['ext'] if 'ext' in jobcard[target] else None
        item_width = jobcard[target]['set_width'] if 'set_width' in jobcard[target] else 3724
        item_height = jobcard[target]['set_height'] if 'set_height' in jobcard[target] else 5616
        item_kbps = jobcard[target]['set_kbps'] if 'set_kbps' in jobcard[target] else None
        
        
    except Exception as e: 
        logger.error("Item values are not properly set, please correct error " + str(e))
        Error = True
        
    #===========================================================================
    # Get Boxcover information from Config
    #===========================================================================
    
    try:
        boxcover_font = config[target]['font'] if "font" in config[target] else None
        boxcover_star_size = config[target]['star_size'] if "star_size" in config[target] else 150
        boxcover_edgeid_size = config[target]['edgeid_size'] if "edgeid_size" in config[target] else 50
        boxcover_support_size = config[target]['support_size'] if "support_size" in config[target] else 120
        boxcover_shortitle_size = config[target]['shorttitle_size'] if "shorttitle_size" in config[target] else 120
        boxcover_title_size = config[target]['title_size'] if "title_size" in config[target] else 160
        boxcover_title_location = config[target]['title_location'] if "title_location" in config[target] else "right"
        boxcover_font_color = config[target]['font_color'] if "font_color" in config[target] else "White"
        boxcover_back_suffix = config[target]['back_suffix'] if "back_suffix" in config[target] else "_back"
        boxcover_density = config[target]['density'] if "density" in config[target] else 72
  
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
    if clip_supporting_name == 'NULL':
        nosupport = True
    else:
        nosupport = False
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
    logger.debug("Gravity " + str(gravity) + " Alignment " + str(item_alignment))

    #===========================================================================
    # Make Boxcover
    #===========================================================================
    RESIZE_IMG = "'" + finaldestination +  "/" + str(edgeid)  + str(item_suffix) + str(boxcover_back_suffix) + item_ext +"'"
    REMOVE_IMG = finaldestination +  "/" + str(edgeid)  + str(item_suffix) + str(boxcover_back_suffix) + item_ext
    BOX_PSD = "'"  + finaldestination +  "/" + str(edgeid)  + str(item_suffix) + ".psd'"
    BOX_IMG = "'" + finaldestination +  "/" + str(edgeid)  + str(item_suffix) + item_ext +"'"
    item_width_delta = item_width - 64
    item_height_delta = item_height - 100
    
    # Create Box Cover Command Template
    CMD_TEMPLATE =  """
            $CONVERT \( -size ${WIDTH}x${HEIGHT} -density $DENSITY -label 'background' -background transparent xc:none -depth 8 -set colorspace:auto-grayscale off  \)  \\
            \( -label 'imageA' '${FINALDESTINATION}/${EDGEID}${SUFFIX}${BACK_SUFFIX}${EXT}' \)  \\
            -label 'title' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity ${TITLE_GRAVITY} -font ${FONT} -pointsize ${TITLESIZE} -fill ${COLOR} label:"${TITLE}" \)  \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \) \\
            -label 'star' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity ${GRAVITY} -font ${FONT} -pointsize ${STARSIZE} -fill ${COLOR} label:'${STAR}' -splice x250 \)  \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \) \\
            -label 'supporting'   \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity ${GRAVITY} -font  ${FONT} -pointsize ${SUPPORTINGSIZE} -fill ${COLOR} label:'${SUPPORTING}' -splice x550 \)  \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \) \\
            -label 'shorttitle' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity west -font ${FONT} -interline-spacing -75 -pointsize ${SHORTTITLESIZE} -fill ${COLOR} label:'${SHORTTITLE}'   \) \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \) \\
            -label 'edgeid' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity Southwest -font ${FONT} -pointsize ${EDGEIDSIZE} -fill ${COLOR} label:'${EDGEID}' \)  \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \)  \\
            -label 'logo' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity SouthEast -font /edge/JobCard2/font/ArialBlack.ttf -pointsize ${EDGEIDSIZE} -interline-spacing -10 -fill ${COLOR} label:'Edge/Picticon' \) \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \)  \\
            -label 'blank' \(  -size ${WIDTH}x${HEIGHT} -background transparent  -gravity SouthEast -font ${FONT} -pointsize ${EDGEIDSIZE} -fill ${COLOR} label:'' \)  \\
            -gravity center -extent ${WIDTH}x${HEIGHT}  ${BOXPSD};  $CONVERT $BOXPSD  -flatten $BOXIMG
            """

    if nosupport:
        CMD_TEMPLATE =  """
        $CONVERT \( -size ${WIDTH}x${HEIGHT} -density $DENSITY -label 'background' -background transparent xc:none -depth 8 -set colorspace:auto-grayscale off  \)  \\
        \( -label 'imageA' '${FINALDESTINATION}/${EDGEID}${SUFFIX}${BACK_SUFFIX}${EXT}' \)  \\
        -label 'title' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity ${TITLE_GRAVITY} -font ${FONT} -pointsize ${TITLESIZE} -fill ${COLOR} label:"${TITLE}" \)  \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \) \\
        -label 'star' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity ${GRAVITY} -font ${FONT} -pointsize ${STARSIZE} -fill ${COLOR} label:'${STAR}' -splice x250 \)  \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \) \\
        -label 'shorttitle' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity west -font ${FONT} -interline-spacing -75 -pointsize ${SHORTTITLESIZE} -fill ${COLOR} label:'${SHORTTITLE}'   \) \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \) \\
        -label 'edgeid' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity Southwest -font ${FONT} -pointsize ${EDGEIDSIZE} -fill ${COLOR} label:'${EDGEID}' \)  \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \)  \\
        -label 'logo' \( \( -size ${WIDTH_DELTA}x${HEIGHT_DELTA}  -background transparent  -gravity SouthEast -font /edge/JobCard2/font/ArialBlack.ttf -pointsize ${EDGEIDSIZE} -interline-spacing -10 -fill ${COLOR} label:'Edge/Picticon' \) \( +clone -background black -shadow 100x3+15+15  \) +swap -composite \)  \\
        -label 'blank' \(  -size ${WIDTH}x${HEIGHT} -background transparent  -gravity SouthEast -font ${FONT} -pointsize ${EDGEIDSIZE} -fill ${COLOR} label:'' \)  \\
        -gravity center -extent ${WIDTH}x${HEIGHT}  ${BOXPSD};  $CONVERT $BOXPSD  -flatten $BOXIMG
        """



    CMD = Template(CMD_TEMPLATE).safe_substitute(CONVERT=CONVERT, ITEM_SOURCE=item_source, WIDTH=item_width, HEIGHT=item_height, GRAVITY=gravity, TITLE_GRAVITY=boxcover_title_location, RESIZETO=resizeto, FINALDESTINATION=finaldestination, EDGEID=edgeid, SUFFIX=item_suffix, BACK_SUFFIX=boxcover_back_suffix, EXT=item_ext, DENSITY=boxcover_density, FONT=boxcover_font, HEIGHT_DELTA=item_height_delta, WIDTH_DELTA=item_width_delta, TITLE=boxcover_title, SHORTTITLE=boxcover_shorttitle, STAR=all_star, SUPPORTING=clip_supporting_name,TITLESIZE=boxcover_title_size,STARSIZE=boxcover_star_size,SUPPORTINGSIZE=boxcover_support_size,SHORTTITLESIZE=boxcover_shortitle_size,EDGEIDSIZE=boxcover_edgeid_size,LOGOSIZE=boxcover_edgeid_size,BOXPSD=BOX_PSD,COLOR=boxcover_font_color,BOXIMG=BOX_IMG)                                             
      
    
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


def exists(dest_vol, target, jobcard, config, volume, noexec):
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
        object_name, object_number = target.split(".")
    except:
        object_name = target
        object_number = "0"
    
    #===========================================================================
    # Item Information for local use
    #===========================================================================
    logger.debug("Set item key value pairs")
    try:
        item_type = jobcard[target]['type'] if 'type' in jobcard[target] else None
        item_action = jobcard[target]['action'] if 'action' in jobcard[target] else None
        item_src = jobcard[target]['src'] if 'src' in jobcard[target] else None
        item_alignment = jobcard[target]['alignment'] if 'alignment' in jobcard[target] else None
        item_name = jobcard[target]['name'] if 'name' in jobcard[target] else None
        item_dir = jobcard[target]['dir'] if 'dir' in jobcard[target] else None
        item_thumbnail = jobcard[target]['thumbnail'] if 'thumbnail' in jobcard[target] else False
        item_watermark = jobcard[target]['watermark'] if 'watermark' in jobcard[target] else False
        item_suffix = jobcard[target]['suffix'] + str(object_number) if 'suffix' in jobcard[target] else "_" + str(object_number)
        item_ext = jobcard[target]['ext'] if 'ext' in jobcard[target] else None
        item_width = jobcard[target]['set_width'] if 'set_width' in jobcard[target] else None
        item_height = jobcard[target]['set_height'] if 'set_height' in jobcard[target] else None
        item_kbps = jobcard[target]['set_kbps'] if 'set_kbps' in jobcard[target] else None
        
        
    except Exception as e: 
        logger.error("Item values are not properly set, please correct error " + str(e))
        Error = True
        
    #===========================================================================
    # Get Boxcover information from Config
    #===========================================================================
    
    try:
        boxcover_font = config[target]['font'] if "font" in config[target] else None
        boxcover_star_size = config[target]['star_size'] if "star_size" in config[target] else 150
        boxcover_edgeid_size = config[target]['edgeid_size'] if "edgeid_size" in config[target] else 50
        boxcover_support_size = config[target]['support_size'] if "support_size" in config[target] else 120
        boxcover_shortitle_size = config[target]['shorttitle_size'] if "shorttitle_size" in config[target] else 120
        boxcover_title_size = config[target]['title_size'] if "title_size" in config[target] else 160
        boxcover_title_location = config[target]['title_location'] if "title_location" in config[target] else "right"
        boxcover_font_color = config[target]['font_color'] if "font_color" in config[target] else "White"
        boxcover_back_suffix = config[target]['back_suffix'] if "back_suffix" in config[target] else "_back"
  
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



def ignore(dest_vol, target, jobcard, config, volume, noexec):
    Error = False
    logger.warn("Ignoring action " + str(object))
    return(Error)


def main(argv=None):
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%s (%s)' % (program_version, program_build_date)
    program_shortdesc = SHORTDESC
    program_license = '''%s
    
  Created by Colin Bitterfield on %s.
  Copyright 2017 Edge Intereactive. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))
    
    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-c","--configfile", dest="config", default="config.yaml", help="use config file, default is config.yml in working dir")
        parser.add_argument("-l","--log", action="store", help="Write Log to location provided, if no file provided use jobcard name and put in local dir" )
        parser.add_argument("-j","--jobcard", action="store", help="task card" )
        parser.add_argument("-n","--noexec", action="store_true", default="False", help="Do not run commands on the OS; echo the command on the OS only" )
        parser.add_argument("-t","--test", action="store_true", help="Test/Validate the Jobcard and exit" )
        parser.add_argument("-d","--debug", action="store", default="INFO", help="set the debug level [INFO, WARN, ERROR, CRITICAL, DEBUG" )
        parser.add_argument("-xp","--noproduct", action="store_true", default="False", help="Don't build products" )
        parser.add_argument("-xc","--nocomponent", action="store_true", default="False", help="Don't build components" )
        parser.add_argument("-sc","--singlecomponent", dest="singlecomponent", action="store", default="False", help="Only work on a single component, adds -xp by default")
        parser.add_argument("-v","--version", dest="showversion", action="store_true", help="Display version and exit")
        parser.add_argument("-a","--action", dest="action", action="store_true", default = 'CREATE' ,help="Action = [CREATE | EXISTS | IGNORE")
        

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    
    except Exception as e:
        print ('Error ' + str(e))
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
        
        
    # Process arguments
    args = parser.parse_args()
    
    if args.showversion == True:
        print(program_name)
        print(program_version_message)
        return 0
    
    configfile = args.config
    logfile = args.log
    jobcardfile = args.jobcard
    NOEXEC = args.noexec if args.noexec else False
    TEST = args.test if args.test else False
    if args.debug:
        DEBUG = True
        DEBUGLEVEL = args.debug
    else:
        DEBUG = False
        DEBUGLEVEL = 'INFO'
    NOPRODUCT = args.noproduct if args.noproduct else False
    NOCOMPONENT = args.nocomponent if args.nocomponent else False
    SINGLECOMPONET = args.singlecomponent if args.singlecomponent else False  
    ACTION = args.action if args.action else 'CREATE' 
    
    
    
     
    #===============================================================================
    # Setup  Logging
    #===============================================================================
    import logging
    import logging.config 
    logger = logging.getLogger(__name__)
    
    
    
    if logfile == None:
        logging.basicConfig(format='%(asctime)s %(name)s:%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=DEBUGLEVEL)
        
    else:
        logging.basicConfig(filename=args.log,format='%(asctime)s %(name)s:%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=DEBUGLEVEL)
        
    logger.debug('CLI Arguements: ' + str(args))
    logger.info("Starting " + str(program_name)) 
    
    return 0    


if __name__ == '__main__': main()
    


