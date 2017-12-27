#!/opt/local/bin/python
# encoding: utf-8
'''
jobrun2 -- shortdesc

jobrun2 is a description

It defines classes_and_methods

@author:     Colin Bitterfield

@copyright:  2017 Edge Intereactive. All rights reserved.

@license:    license

@contact:    colin@bitterfield.com
@deffield    updated: Updated
'''


import yaml
import subprocess
import os
import sys
import argparse
import shlex
import datetime
import importlib
import task




from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2017-12-10'
__updated__ = '2017-12-10'

DEBUG = 0
TESTRUN = 0
PROFILE = 0
DEST_VOL = "assembly"

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
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
        parser.add_argument("-l","--log", action="store", help="Write List of CSV files and information if ommitted write file named same as task card" )
        parser.add_argument("-j","--jobcard", action="store", help="task card" )
        parser.add_argument("-n","--noexec", action="store_true", help="Do not run commands on the OS; echo the command on the OS only" )
        parser.add_argument("-t","--test", action="store_true", help="Test/Validate the Jobcard and exit" )
        parser.add_argument("-d","--debug", action="store", help="set the debug level [INFO, WARN, ERROR, CRITICAL, DEBUG" )
        parser.add_argument("-xp","--noproduct", action="store_true", help="Don't build products" )
        parser.add_argument("-xc","--nocomponent", action="store_true", help="Don't build components" )
        parser.add_argument("-sc","--signcomponent", dest="single", action="store", help="Only work on a single component, adds -xp by default")
        
 
        # Process arguments
        args = parser.parse_args()


    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    # Start Main Code
    Error = False
    #===============================================================================
    # Setup  Logging
    #===============================================================================
    import logging
    import logging.config 
    logger = logging.getLogger(__name__)
    
    if not args.log == None:
        
        logging.basicConfig(filename=args.log, disable_existing_loggers=False,format='%(asctime)s %(name)s:%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=args.debug)
    else:
        logging.basicConfig(disable_existing_loggers=False,format='%(asctime)s %(name)s:%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=args.debug)
    
    logger.info("ARGS:" + str(args))
        
    # Check for minimum requirements
    if args.jobcard == None:
        logger.error("Please provide a valid Job card: this is required")
        print parser.parse_args(['-h'])
        exit(1)
    else:
        if os.path.isfile(args.jobcard):
            logger.info("Job Card Exists: " + args.jobcard)
            job = open(args.jobcard,'r')
            jobcard = yaml.load(job)
        else:
            logger.error("Job card missing")
            print parser.parse_args(['-h'])
            exit(1)

    if os.path.isfile(args.config):
        logger.info("Config file exists" + args.config)
        cfg = open(args.config,'r')
        config = yaml.load(cfg)
    else:
        logger.error("Missing Config File" + args.config)
        print parser.parse_args(['-h'])
        exit(2) 

    volume_list = config['default']['volume'] if 'volume' in config['default'] else None
    if volume_list == None:
        logger.error("Missing Volume List")
        logger.info("Check config file for proper configuration")
    elif not os.path.isfile(volume_list):
        logger.error("Bad or malformed Volume List")
        logger.info("Check config file for proper configuration")
    else:
        vol = open(volume_list, 'r')
        volume = yaml.load(vol)
    
    
            
    

    products = task.makeList(jobcard, 'product')
    logger.info("Products to create: " + str(products))
    
    if args.single:
        components = []
        logger.info("Running in single Component Mode for component " + str(args.single))
        components.append(args.single)
    else:
        components = task.makeList(jobcard, 'component')
        logger.info("Components to create: " + str(components))
    
    # Evaluate the Components
    for test_component in components:
        #logger.info("Testing Component " + str(test_component))
        myError = task.validateitem(config, jobcard, volume, test_component)
        Error = myError if Error is False else True
    
    
    # Run Component Jobs
    if not args.nocomponent:
        logger.info("Running component jobs")
        for component in sorted(components):
            logger.debug("component " + str(component))   
            try:
                base_component, component_modifier = component.split(".")
                item_module = config[base_component]["module"] if "module" in config[base_component] else None
            except Exception as e:  
                item_module = config[component]["module"] if "module" in config[component] else None
                
            logger.debug("Module for production is " + str(item_module))
            myModule = importlib.import_module(item_module)
            jobflag = jobcard[component]['action']     
            if jobflag == 'produce':
                myError = myModule.produce(DEST_VOL,component, jobcard, config, volume, args.noexec)
            elif jobflag == 'exists':
                myError = myModule.exists(DEST_VOL,component, jobcard, config, volume, args.noexec)
            else:
                myError = myModule.ignore(DEST_VOL,component, jobcard, config, volume, args.noexec)    
    
            Error = myError if Error is False else True
    
    
    
    # Run Product Jobs
    if not args.noproduct:
        logger.info("Running product jobs")
        
    
    
    
    
    if Error:
        logger.error("Validation Failed")
        logger.error("Fix errors and re-run")
        exit(1)
    
    if args.test:
        logger.warn("Validation test only")
        exit(0)
    
    
    logger.info("Program run completed")
    if Error:
        logger.error("Program completed with errors")
    else:
        logger.info("Program completed without errors")
    return Error
    
    
    
    
    
    
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'jobrun2_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())