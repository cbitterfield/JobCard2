#!/usr/bin/python

'''
Created on Sep 30, 2017

@author: colin
'''

#===============================================================================
# Import 
#===============================================================================

import os
from string import Template
import task
import yaml



#===============================================================================
# Setup  Logging
#===============================================================================
import logging
import logging.config 
logger = logging.getLogger(__name__)
    

logging.basicConfig(disable_existing_loggers=False,format='%(asctime)s %(name)s:%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="DEBUG")
    
#===============================================================================
#  Load JobCard and Config
#===============================================================================
        
cfg = open('./example/config.yaml','r')
config = yaml.load(cfg)
logger.info(config)

job = open('./example/edge0022_rc2.yaml','r')
jobcard = yaml.load(job)
logger.info(jobcard)

#===============================================================================
# Test Code Block
#===============================================================================

noexec = False

logger.info("Testing a task --")


subject = " Send Alerts from Python"
message = "Automated Alert from Python Program"

Error = task.sendeMail(config,"Jobcard Completion " , "Program completed with errors")


logger.info (Error)
logger.info("End Testing a task")