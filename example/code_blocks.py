# Variables for standard use:

config = {}
jobcard = {}
noexec = True
command = {}
command_status = {}
command_name = "example"
CMD = ''
item_src = ''

# Standard Imports
import os
import job
import logging
import subprocess


logger = logging.getLogger(__name__)



# Code Block - Run a command an check results

# 
command_name = 'MyCommand'

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

boxcover: 
     type: component
     action: produce
     src: C1E253-C1E258/C1E255_COMBAT_ZONE-682/BoxCovers/GMCZ0022_DONNA_BELL__CHOKY_ICE_22.jpg
     alignment: right
     name: boxcover
     thumbnail: False
     suffix: _boxcover
     ext: .jpg
     set_width: 3724
     set_height: 5616

# Item Codeblock


object = "Working Object, component or product"

try:
    object_base, object_modifier = object.split(".")

except
    object_base = object



try:
    item_type = jobcard[object]['type'] if 'type' in jobcard[object] else None
    item_action = jobcard[object]['action'] if 'action' in jobcard[object] else None
    item_src = jobcard[object]['src'] if 'src' in jobcard[object] else None
    item_alignment = jobcard[object]['alignment'] if 'alignment' in jobcard[object] else None
    item_name = jobcard[object]['name'] if 'name' in jobcard[object] else None
    item_dir = jobcard[object]['dir'] if 'dir' in jobcard[object] else None
    item_thumbnail = jobcard[object]['thumbnail'] if 'thumbnail' in jobcard[object] else False
    item_watermark = jobcard[object]['watermark'] if 'watermark' in jobcard[object] else False
    item_suffix = jobcard[object]['suffix'] if 'suffix' in jobcard[object] else None
    item_ext = jobcard[object]['ext'] if 'ext' in jobcard[object] else None
    item_width = jobcard[object]['set_width'] if 'set_width' in jobcard[object] else None
    item_height = jobcard[object]['set_height'] if 'set_height' in jobcard[object] else None
    item_kbps = jobcard[object]['set_kbps'] if 'set_kbps' in jobcard[object] else None
    
    
except Exception as e: 
    logger.error("Item values are not properly set, please correct error " + str(e))
    Error = True
    
# Test Required Parameters

if item_type == None or item_action == None or item_src == None:
    Error = True
    logger.error ("Required key values are missing")
    logger.error ("type = " + str(item_type) + " , action = " + str(item_action) + " , source = " + str(item_src))

else:
    Error = False
    logger.info ("Item values are set properly and requirements are met")
    logger.debug("Type :" + str(item_type))
    logger.debug("Action :" + str(item_action))
    logger.debug("Source :" + str(item_src))
    logger.debug("Alignment :" + str(item_alignment))
    logger.debug("Name :" + str(item_name))
    logger.debug("Directory :" + str(item_dir))
    logger.debug("set_height :" + str(item_height))
    logger.debug("set_width :" + str(item_width))
    logger.debug("set_kbps :" + str(item_kbps))
    logger.debug("Suffix :" + str(item_suffix))
    logger.debug("Extension :" + str(item_ext))
    logger.debug("Thumbnail :" + str(item_thumbnail))
    logger.debug("Watermark :" + str(item_watermark))
    
    
    try    
        # Get Clip Information 
        clip_prime_dubya = jobcard['clipinfo']['prime_dubya']
        clip_edgeid = = jobcard['clipinfo']['edgeid']
        clip_shorttitle = jobcard['clipinfo']['shorttitle']
        clip_title = jobcard['clipinfo']['title']
        clip_description = jobcard['clipinfo']['description']
        clip_keywords = jobcard['clipinfo']['keywords']
        clip_productiondate = jobcard['clipinfo']['productiondate']
        clip_releasedate = jobcard['clipinfo']['releasedate']
        clip_licensor = jobcard['clipinfo']['licensor']
        clip_comment = jobcard['clipinfo']['comment']
        clip_star_name = jobcard['clipinfo']['star']['name'] if "name" in jobcard['clipinfo']['star'] else ''
        clip_star_birthdate = jobcard['clipinfo']['star']['birthdate'] if "birthdate" in jobcard['clipinfo']['star'] else None
        clip_star_age = jobcard['clipinfo']['star']['age'] if "age" in jobcard['clipinfo']['star'] else None
        clip_star_height = jobcard['clipinfo']['star']['height'] if "height" in jobcard['clipinfo']['star'] else None
        clip_star_weight = jobcard['clipinfo']['star']['weight'] if "weight" in jobcard['clipinfo']['star'] else None
        clip_star_measurements = jobcard['clipinfo']['star']['measurements'] if "measurements" in jobcard['clipinfo']['star'] else None
        clip_star_hair = jobcard['clipinfo']['star']['hair'] if "hair" in jobcard['clipinfo']['star'] else None
        clip_star_eyes = jobcard['clipinfo']['star']['eyes'] if "eyes" in jobcard['clipinfo']['star'] else None
        clip_star_skin = jobcard['clipinfo']['star']['skin'] if "skin" in jobcard['clipinfo']['star'] else None
        clip_star_birthplace = jobcard['clipinfo']['star']['birthplace'] if "birthplace" in jobcard['clipinfo']['star'] else None            
        clip_star2 = True if "star2" in jobcard['clipinfo'] else False
        if clip_star2:
            logger.info("Loading Star 2")
            clip_star2_name = jobcard['clipinfo']['star2']['name'] if "name" in jobcard['clipinfo']['star2'] else ''
            clip_star2_birthdate = jobcard['clipinfo']['star2']['birthdate'] if "birthdate" in jobcard['clipinfo']['star2'] else None
            clip_star2_age = jobcard['clipinfo']['star2']['age'] if "age" in jobcard['clipinfo']['star2'] else None
            clip_star2_height = jobcard['clipinfo']['star2']['height'] if "height" in jobcard['clipinfo']['star2'] else None
            clip_star2_weight = jobcard['clipinfo']['star2']['weight'] if "weight" in jobcard['clipinfo']['star2'] else None
            clip_star2_measurements = jobcard['clipinfo']['star2']['measurements'] if "measurements" in jobcard['clipinfo']['star2'] else None
            clip_star2_hair = jobcard['clipinfo']['star2']['hair'] if "hair" in jobcard['clipinfo']['star2'] else None
            clip_star2_eyes = jobcard['clipinfo']['star2']['eyes'] if "eyes" in jobcard['clipinfo']['star2'] else None
            clip_star2_skin = jobcard['clipinfo']['star2']['skin'] if "skin" in jobcard['clipinfo']['star2'] else None
            clip_star2_birthplace = jobcard['clipinfo']['star2']['birthplace'] if "birthplace" in jobcard['clipinfo']['star2'] else None
        clip_supporting_name = jobcard['clipinfo']['supporting']['name'] if "name" in jobcard['clipinfo']['supporting'] else ''
        clip_supporting_birthdate = jobcard['clipinfo']['supporting']['birthdate'] if "birthdate" in jobcard['clipinfo']['supporting'] else None
        clip_supporting_age = jobcard['clipinfo']['supporting']['age'] if "age" in jobcard['clipinfo']['supporting'] else None
        clip_supporting_height = jobcard['clipinfo']['supporting']['height'] if "height" in jobcard['clipinfo']['supporting'] else None
        clip_supporting_weight = jobcard['clipinfo']['supporting']['weight'] if "weight" in jobcard['clipinfo']['supporting'] else None
        clip_supporting_measurements = jobcard['clipinfo']['supporting']['measurements'] if "measurements" in jobcard['clipinfo']['supporting'] else None
        clip_supporting_hair = jobcard['clipinfo']['supporting']['hair'] if "hair" in jobcard['clipinfo']['supporting'] else None
        clip_supporting_eyes = jobcard['clipinfo']['supporting']['eyes'] if "eyes" in jobcard['clipinfo']['supporting'] else None
        clip_supporting_skin = jobcard['clipinfo']['supporting']['skin'] if "skin" in jobcard['clipinfo']['supporting'] else None
        clip_supporting_birthplace = jobcard['clipinfo']['supporting']['birthplace'] if "birthplace" in jobcard['clipinfo']['supporting'] else None
              
        
    except Exception as e:  
        logger.warning("Not all clip variables set properly; exception " + str(e)) 
        Error = True      
    
    # Show Clip variables
    logger.info("Clip description " + str(item_title) + " Edge ID: " + str(clip_edgeid))
    logger.info("Star " + str(clip_star_name))
    if clip_star2:
        logger.info("Star2 " + str(clip_star2_name))
    logger.info("Supporting: " + str(clip_supporting_name)) 
    logger.info("Short Title: " + str(clip_shorttitle))
    
    
    
    
    
    
    
    
    
    
        