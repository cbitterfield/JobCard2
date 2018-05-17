#!/usr/bin/python

'''
Created on Sep 30, 2017

@author: colin
'''

#===============================================================================
# Import 
#===============================================================================

import os
import task
import yaml
import sys



#===============================================================================
# Setup  Logging
#===============================================================================
import logging
import logging.config 
logger = logging.getLogger(__name__)
    

logging.basicConfig(disable_existing_loggers=False,format='%(asctime)s %(name)s:%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="DEBUG")
    
DEBUG=0
TESTRUN=0
program_name = os.path.basename(sys.argv[0])


#===============================================================================
# Test Code Block
#===============================================================================

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i","--input", help="Input directory")
parser.add_argument("-o","--output", help="output directory")


 
# Process arguments
args = parser.parse_args()

if not args.input and not args.outdir:
    print ("ERROR")
    exit(1)

print args

if os.path.isdir(args.input):
    print "Input directory exists"
else:
    print "Input directory does not exist"
    exit (1)


if os.path.isdir(args.output):
    print "output directory exists"
else:
    print "output directory does not exist"
    exit (1)


for product in os.listdir(args.input):
    if os.path.isdir(args.input + "/" + product):
        print product
    else:
        print "Not a directory =>" + str(product)


mkisofs -J -r -o /edge/Scratch/TEST_ROM.iso -V TEST_ROM -uid 500 -find 
        