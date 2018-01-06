#-*- coding: utf-8 -*-
'''
Created on Sep 30, 2017

@author: colin
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

def word_wrap(string, width=80, ind1=0, ind2=0, prefix=''):
    """ word wrapping function.
        string: the string to wrap
        width: the column number to wrap at
        prefix: prefix each line with this string (goes before any indentation)
        ind1: number of characters to indent the first line
        ind2: number of characters to indent the rest of the lines
    """
    string = prefix + ind1 * " " + string
    newstring = ""
    while len(string) > width:
        # find position of nearest whitespace char to the left of "width"
        marker = width - 1
        while not string[marker].isspace():
            marker = marker - 1

        # remove line from original string and add it to the new string
        newline = string[0:marker] + "\n"
        newstring = newstring + newline
        string = prefix + ind2 * " " + string[marker + 1:]

    return newstring + string



def produce(dest_vol, object, jobcard, config, volume, noexec):
    Error = False
    
    logger.debug("Destination Volume " + str(dest_vol))
    logger.debug("Object " + str(object))
    logger.debug("Jobcard " + str(jobcard))
    logger.debug("Config " + str(config))
    logger.debug("Volume " + str(volume))
    logger.debug("NoExec " + str(noexec))
    
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
        item_suffix = jobcard[object]['suffix'] if 'suffix' in jobcard[object] else None
        item_ext = jobcard[object]['ext'] if 'ext' in jobcard[object] else None
        item_width = jobcard[object]['set_width'] if 'set_width' in jobcard[object] else None
        item_height = jobcard[object]['set_height'] if 'set_height' in jobcard[object] else None
        item_kbps = jobcard[object]['set_kbps'] if 'set_kbps' in jobcard[object] else None
        
        
    except Exception as e: 
        logger.error("Item values are not properly set, please correct error " + str(e))
        Error = True
        
    
    #===========================================================================
    # Clip Information
    #===========================================================================
    logger.debug("Set clipinfo key value pairs")
    
    try:    
    # Get Clip Information 
        clip_prime_dubya = jobcard['clipinfo']['prime_dubya']
        clip_edgeid = jobcard['clipinfo']['edgeid']
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
    logger.info("Clip description " + str(clip_title) + " Edge ID: " + str(clip_edgeid))
    logger.info("Star " + str(clip_star_name))
    if clip_star2:
        logger.info("Star2 " + str(clip_star2_name))
    logger.info("Supporting: " + str(clip_supporting_name)) 
    logger.info("Short Title: " + str(clip_shorttitle))
    
    
    
    
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
    
    
   
   

    #===========================================================================
    # Create text file from template
    #===========================================================================
    template = open(item_source,"r")
    if not noexec:
        puttext = open(str(finaldestination) + "/" + str(edgeid) + str(item_suffix) + str(item_ext), "w")
    
    for line in template:
        if clip_star2:      
            replaced_line = Template(line).safe_substitute(EDGEID=edgeid, SUPPORTING=clip_supporting_name,SHORTTITLE=clip_shorttitle, KEYWORDS=clip_keywords, PRODUCTIONDATE=clip_productiondate, RELEASEDATE=clip_releasedate, LICENSOR=clip_licensor, PROJECTNO=projectno, DESCRIPTION=clip_description, TITLE=clip_title, PRIME_DUBYA=clip_prime_dubya, STAR=clip_star_name, STAR_BIRTHDATE=clip_star_birthdate, STAR_AGE=clip_star_age, STAR_HEIGHT=clip_star_height, STAR_WEIGHT=clip_star_weight, STAR_MEASUREMENTS=clip_star_measurements, STAR_HAIR=clip_star_hair, STAR_EYES=clip_star_eyes, STAR_SKIN=clip_star_skin, STAR_BIRTHPLACE=clip_star_birthplace, STAR2=clip_star2_name, STAR2_BIRTHDATE=clip_star2_birthdate, STAR2_AGE=clip_star2_age, STAR2_HEIGHT=clip_star2_height, STAR2_WEIGHT=clip_star2_weight, STAR2_MEASUREMENTS=clip_star2_measurements, STAR2_HAIR=clip_star2_hair, STAR2_EYES=clip_star2_eyes, STAR2_SKIN=clip_star2_skin, STAR2_BIRTHPLACE=clip_star2_birthplace)
        else:
            replaced_line = Template(line).safe_substitute(EDGEID=edgeid, SUPPORTING=clip_supporting_name,SHORTTITLE=clip_shorttitle, KEYWORDS=clip_keywords, PRODUCTIONDATE=clip_productiondate, RELEASEDATE=clip_releasedate, LICENSOR=clip_licensor, PROJECTNO=projectno, DESCRIPTION=clip_description, TITLE=clip_title, PRIME_DUBYA=clip_prime_dubya, STAR=clip_star_name, STAR_BIRTHDATE=clip_star_birthdate, STAR_AGE=clip_star_age, STAR_HEIGHT=clip_star_height, STAR_WEIGHT=clip_star_weight, STAR_MEASUREMENTS=clip_star_measurements, STAR_HAIR=clip_star_hair, STAR_EYES=clip_star_eyes, STAR_SKIN=clip_star_skin, STAR_BIRTHPLACE=clip_star_birthplace, )

        formatted_line = word_wrap(replaced_line, width=115, ind1=0, ind2=11, prefix='')
        
        if not noexec:
            puttext.write(formatted_line)
        else:
            logger.debug(formatted_line)

    
    if not noexec:
        puttext.close()
    
    template.close()

    

    logger.info("Module ending for action produce")
    logger.debug("Error " + str(Error))
    return(Error)


def exists(dest_vol,component, jobcard, config, volume, noexec):
    Error = True
    logger.error("Not a valid action")
    return(Error)



def ignore(dest_vol,component, jobcard, config, volume, noexec):
    Error = False
    logger.warn("Ignoring action " + str(component))
    return(Error)