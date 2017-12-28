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
        puttext = open(finaldestination + "/" + edgeid + item_suffix + item_ext, "w")
    
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
    logger.info("exists action")
    return(Error)



def ignore(dest_vol,component, jobcard, config, volume, noexec):
    Error = False
    logger.warn("Ignoring action " + str(component))
    return(Error)