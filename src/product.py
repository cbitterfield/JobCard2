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





def produce(source_vol, dest_vol, object, jobcard, config, volume, components, noexec):
    Error = False
    import task
    import shutil
    
    logger.debug("Start job for " + str(object))
    #===========================================================================
    # Load needed programs
    #===========================================================================
    
    MKISOFS = config['programs']['mkisofs']
    
    
    logger.debug("Destination Volume " + str(dest_vol))
    logger.debug("Object " + str(object))
    logger.debug("Jobcard " + str(jobcard))
    logger.debug("Config " + str(config))
    logger.debug("Source Volume " + str(source_vol))
    logger.debug("Destination Volume " + str(dest_vol))
    logger.debug("NoExec " + str(noexec))
    
    #===========================================================================
    # Item Information for local use
    #===========================================================================
    logger.debug("Set Product key value pairs")
    try:
        product_type = jobcard[object]['type'] if "type" in jobcard[object] else None
        product_action = jobcard[object]['action'] if "action" in jobcard[object] else None
        product_account = jobcard[object]['account'] if "account" in jobcard[object] else None
        product_name = jobcard[object]['name'] if "name" in jobcard[object] else None
        product_dir = jobcard[object]['dir'] if "dir" in jobcard[object] else None
        
        
    except Exception as e: 
        logger.error("Product values are not properly set, please correct error " + str(e))
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
    
    #finaldestination = destination + "/" + str(product_name)
        #setup final destination in complex situations
    if not product_name == None and not product_dir == None:
        finaldestination = destination + "/" + str(product_name) + "/" + str(product_dir)
    elif not product_name == None and product_dir == None:
        finaldestination = destination + "/" + str(product_name)
    elif product_name == None and not product_dir == None:
        finaldestination = destination + "/" + str(product_dir)     
    else:
        finaldestination = destination
    
    
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
    logger.info("Product: " + str(object))
    logger.info("Name Dir: " + str(product_name))
    
    #===========================================================================
    # Make map list
    #===========================================================================
    dir_map = {}
    for product_value in jobcard[object]:
        logger.debug("Evaluate each entry for map " + str(product_value))
        if product_value.startswith("map_"):
            logger.debug("Mapped dir " + str(product_value))
            nul_map, mapped = product_value.split("_")
            dir_map[mapped] = jobcard[object][product_value] if product_value in jobcard[object] else "./"
    logger.debug(dir_map)
    
    #===========================================================================
    # Make sure each component has a mapped value
    #===========================================================================
    for component in components:
        try:
            if not dir_map[component]:
                dir_map[component] = "./"

        except Exception as e: 
            logger.warning("Setting default map for " + str(e))
            dir_map[component] = "./"
    #===========================================================================
    # Process each component
    #===========================================================================
    for component in components:
        logger.debug("Process component " + str(component))
        try:
            product_process = jobcard[object][component] if component in jobcard[object] else False
            if product_process:
                logger.debug("Product Process " + str(component) + " => " + str(product_process))
                if dir_map[component]:
                    logger.debug("Mapped to " + str(dir_map[component]))
                if "." in component:
                    component_name, component_value = component.split(".")
                    component_len_value = len(component_value)
                    if not task.number_exists(component_value[component_len_value - 1]):
                        component_value = ""
                else:
                    component_value = 0
                    
                logger.debug("MAP " + str(dir_map))
                #===============================================================
                # Get Component information
                #===============================================================
                component_name = jobcard[component]['name'] if "name" in jobcard[component] else None
                component_dir = jobcard[component]['dir'] if "dir" in jobcard[component] else None
                component_suffix = jobcard[component]['suffix'] + str(component_value) if "suffix" in jobcard[component] else "_" + str(component_value)
                component_ext = jobcard[component]['ext'] if "ext" in jobcard[component] else None
                
                logger.debug("Component Name: " + str(component_name))
                logger.debug("Component Dir " + str(component_dir))
                logger.debug("Component Suffix " + str(component_suffix))
                logger.debug("Component Ext " + str(component_ext))
                
                
                
                #===============================================================
                # Derive the component destination
                #===============================================================
                component_destination = config['default'][source_vol] + "/" + projectno + "/" + prime_dubya + "/" + edgeid if source_vol in config['default'] else None
                if not component_name == None and not component_dir == None:
                    component_finaldestination = component_destination + "/" + str(component_name) + "/" + str(component_dir)
                elif not component_name == None and component_dir == None:
                    component_finaldestination = component_destination + "/" + str(component_name)
                elif component_name == None and not component_dir == None:
                    component_finaldestination = component_destination + "/" + str(component_dir)     
                else:
                    component_finaldestination = component_destination
                logger.debug("Component Source Location " + str(component_finaldestination))
                
                #===============================================================
                # Check each file to see if it matches the suffix and extenstion
                # of the component
                #===============================================================
                logger.debug("Look for needed files matching " + str(component_suffix) + str(component_ext) )
                for markFile in os.listdir(component_finaldestination):
                    if str(component_suffix) in markFile and str(component_ext) in markFile:
                        logger.debug("Found needed file " + str(markFile))
                        logger.info("Copy " + str(component_finaldestination) +"/" + markFile + " => " + str(finaldestination) + "/" + dir_map[component])
                        if not os.path.isdir(str(finaldestination) + "/" + dir_map[component] + "/") and not noexec:
                            os.makedirs(str(finaldestination) + "/" + dir_map[component] + "/")
                            
                        shutil.copy(str(component_finaldestination) +"/" + markFile, str(finaldestination) + "/" + dir_map[component] + "/")  if not noexec else logger.info("Noexec Flag")
            
            else:
                logger.debug("Product Process " + str(component) + " => " + str(product_process))    
    
        except Exception as e: 
            logger.warning("Component problem " + str(e))
            
    
    logger.info("Process each product as needed")
   
    if object == 'ebay':
        logger.info("Processing eBay")
        logger.info("Doing the Ebay thing")
        logger.info("Creating DVD Image")
        logger.info("ISO Destination " + str(finaldestination))
        CMD = MKISOFS + " -J -r -o " + destination + "/" + str(product_name) + "/" + edgeid + "_ROM.iso -V " + edgeid + "_ROM -uid 500 -find " + finaldestination
    
        logger.info("DVD Creation Command: " + CMD)
    
        if not noexec:                
            result = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdoutdata, stderrdata = result.communicate()
            status = result.returncode 
            if status == 0:
                logger.info("DVD Creation returned Status: " + str(status))
            else:
                logger.warning("DVD Creation failed with Status:"+ str(status))
                Error = True 
        else:
            logger.info("Make ISO CMD: " + str(CMD))
        
    if object == 'clips4sale':
        logger.info("Processing Clips4Sale")
        logger.info("Using account " + str(product_account))
        product_password = config[object][product_account] if product_account in config[object] else False
        logger.debug("Using password " + str(product_password))
        product_site = config[object]['ftpsite'] if 'ftpsite' in config[object] else False
        logger.info("Transfer host " + str(product_site))
        # Make a list of Files
        for root, mydirs, files in os.walk(finaldestination):
            for name in files:
                ftp_filename = str(root) + "/" + str(name)
                short_name = ftp_filename.replace(finaldestination,"")
                transfer_dir = os.path.dirname(short_name)
                transfer_file = os.path.basename(short_name)
                if product_password and product_site and not noexec:
                    logger.info("Transfer of files starting")
                    logger.debug("Directories to transfer " + str(transfer_dir))
                    logger.debug("FTP => " + str(finaldestination + "/" + transfer_dir) + " <= " + str(transfer_file))
                    Error = task.filetransfer(product_account, product_password, product_site, finaldestination + "/" + transfer_dir + "/" + transfer_file, transfer_dir)
                else:
                    logger.warn("NOEXEC - Transfer of files starting")
                    logger.debug("Directories to transfer " + str(transfer_dir))
                    logger.debug("FTP => " + str(finaldestination + "/" + transfer_dir) + " <= " + str(transfer_file))  
                    

     
    if object == 'iwantclips':
        logger.info("Processing iwantclips")
        logger.info("Using account " + str(product_account))
        product_password = config[object][product_account] if product_account in config[object] else False
        logger.debug("Using password " + str(product_password))
        product_site = config[object]['ftpsite'] if 'ftpsite' in config[object] else False
        logger.info("Transfer host " + str(product_site))
           # Make a list of Files
        for root, mydirs, files in os.walk(finaldestination):
            for name in files:
                ftp_filename = str(root) + "/" + str(name)
                short_name = ftp_filename.replace(finaldestination,"")
                transfer_dir = os.path.dirname(short_name)
                transfer_file = os.path.basename(short_name)
                if product_password and product_site and not noexec:
                    logger.info("Transfer of files starting")
                    logger.debug("Directories to transfer " + str(transfer_dir))
                    logger.debug("FTP => " + str(finaldestination + "/" + transfer_dir + "/" + str(transfer_file)) + "=> " + str(transfer_dir) + " <= " + str(transfer_file))
                    Error = task.filetransfer(product_account, product_password, product_site, finaldestination + "/" + transfer_dir + "/" + transfer_file, transfer_dir)
                else:
                    logger.warn("NOEXEC - Transfer of files starting")
                    logger.debug("Directories to transfer " + str(transfer_dir))
                    logger.debug("FTP => " + str(finaldestination + "/" + transfer_dir) + " <= " + str(transfer_file))  
 
        
    if object == 'flickrocket':
        logger.info("Processing Flick Rocket")
        

 

    

    logger.info("Module ending for action produce")
    logger.debug("Error " + str(Error))
    return(Error)


def exists(source_vol, dest_vol, object, jobcard, config, volume, components, noexec):
    Error = True
    logger.error ("Not a valid option in this version")
    logger.info("exists action")
    return(Error)



def ignore(source_vol, dest_vol, object, jobcard, config, volume, components, noexec):
    Error = False
    logger.warn("Ignoring action " + str(object))
    return(Error)