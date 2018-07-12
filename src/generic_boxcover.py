#!/usr/bin/python
#-*- coding: utf-8 -*-

'''


generic_boxcover -- shortdesc

generic_boxcover is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2018 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
from subprocess import Popen, PIPE, STDOUT
import subprocess
import csv
from string import Template


from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2018-05-13'
__updated__ = '2018-05-13'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

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

  Created by user_name on %s.
  Copyright 2018 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-c","--filecovers", dest="covers", default="covers.csv", help="List of covers to build")
        parser.add_argument("-i","--image", action="store", help="Image file for base" )
        parser.add_argument("-o","--output", dest="destination", action="store", help="Output directory" )
        parser.add_argument("-d","--debug", action="store", help="set the debug level [INFO, WARN, ERROR, CRITICAL, DEBUG" )
        parser.add_argument("-n","--noexec", action="store_true", help="Do not run commands on the OS; echo the command on the OS only" )
        parser.add_argument("-l","--log", action="store", help="Write List of CSV files and information if ommitted write file named same as task card" )

        # Process arguments
        args = parser.parse_args()

        covers = args.covers.decode('utf-8', 'ignore')
        image_name = args.image
        debug = args.debug
        noexec = args.noexec
        destination = args.destination
        
        item_suffix = '_BOXCOVER'
        item_ext = '.jpg'
        Error = False
        
     

        
        
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
    #===========================================================================
    # Start Main Code
    #===========================================================================
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
    
    logger.debug("ARGS:" + str(args))
    
    logger.info("Starting Creation")
    
    logger.info( "Main Program"   ) 
    
    logger.debug("Cover File: " + covers)
    if noexec:
        logger.debug("Noexec: ")
    else:
        logger.debug("Running Commands")
    logger.debug("Image File: " + image_name)
    logger.debug("destination: " + destination)
    
    #===========================================================================
    # Find Convert program on local machine
    #===========================================================================
    env = os.environ.copy()
    env['PYTHONPATH'] = ":" .join(sys.path) 
    logger.debug('Find Convert Program')
    cmd = 'which convert'
    logger.debug('Run Command [' + str(cmd) + ']')
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    CONVERT = p.stdout.read().rstrip()
    logger.debug (CONVERT)

    #===========================================================================
    # Read the CSV File in for creating box covers (loop through the entries)
    #===========================================================================
    logger.info('CSV File: ' + str(covers))
    
    with open(covers, 'rb') as csvfile:
        make_covers = csv.reader(csvfile, delimiter=',', quotechar='"')
        for boxcover in make_covers:
            logger.info('Making Boxcover for ' + str(boxcover))


            boxcover_font = '/edge/JobCard2/font/ArialBlack.ttf'
            boxcover_star_size = 140
            boxcover_edgeid_size = 50
            boxcover_support_size = 100
            boxcover_shortitle_size = 200
            boxcover_title_size = 110
            boxcover_title_location = 'right'
            boxcover_font_color = 'white'
            boxcover_back_suffix = '_source'
            boxcover_density = 72
            titlegravity = 'North'
         
            #===========================================================================
            # Clean up the title and short title for apostophes
            # Set up proper padding for Star and or Star2
            # Resize source image
            #===========================================================================
            
            boxcover_title = boxcover[0].lstrip().rstrip().replace("'","\\'")
            boxcover_shorttitle = boxcover[1].lstrip().rstrip().replace(",","\\n")
            edgeid = boxcover[4].lstrip().rstrip()
            item_alignment = boxcover_title_location
            clip_star_name = boxcover[2].lstrip().rstrip()
            clip_supporting_name = boxcover[3].lstrip().rstrip()
            if clip_supporting_name == 'NULL':
                nosupport = True
            else:
                nosupport = False
            
            
            
            clip_star2 = False
            item_height = 2048
            item_width = 1440
            item_ext = '.jpg'
            
            if item_alignment == 'left':
                boxcover_title = " " + boxcover_title
                if clip_star2:
                    all_star = " " + clip_star_name + " & " 
                else:
                    all_star = " " + clip_star_name
                supporting = "  " + clip_supporting_name
                gravity='Northwest'
            if item_alignment == 'center':
                gravity = 'North'
                if clip_star2:
                    all_star = clip_star_name + " & " 
                else:
                    all_star = clip_star_name
            if item_alignment == 'right':
                gravity='NorthEast'       
                boxcover_title = boxcover_title + " "
                if clip_star2:
                    all_star = clip_star_name + " & " +  " "
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
            
            logger.info('Preparing background for ' + edgeid)
            
            # Set some more variables as needed
            item_source = image_name
            finaldestination = destination 
            
            
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
                logger.debug("Running Command - " + str(command_name))  
                command[command_name] = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
                logger.info( "COMMAND" + command_name + " for "+ edgeid + " Started" )
                
            
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
            REMOVE_PSD = finaldestination +  "/" + str(edgeid)  + str(item_suffix) + '.psd'
            item_width_delta = item_width - 64
            item_height_delta = item_height - 100

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



            CMD = Template(CMD_TEMPLATE).safe_substitute(CONVERT=CONVERT, ITEM_SOURCE=item_source, WIDTH=item_width, HEIGHT=item_height, GRAVITY=gravity, TITLE_GRAVITY=titlegravity, RESIZETO=resizeto, FINALDESTINATION=finaldestination, EDGEID=edgeid, SUFFIX=item_suffix, BACK_SUFFIX=boxcover_back_suffix, EXT=item_ext, DENSITY=boxcover_density, FONT=boxcover_font, HEIGHT_DELTA=item_height_delta, WIDTH_DELTA=item_width_delta, TITLE=boxcover_title, SHORTTITLE=boxcover_shorttitle, STAR=all_star, SUPPORTING=clip_supporting_name,TITLESIZE=boxcover_title_size,STARSIZE=boxcover_star_size,SUPPORTINGSIZE=boxcover_support_size,SHORTTITLESIZE=boxcover_shortitle_size,EDGEIDSIZE=boxcover_edgeid_size,LOGOSIZE=boxcover_edgeid_size,BOXPSD=BOX_PSD,COLOR=boxcover_font_color,BOXIMG=BOX_IMG)                                             
                
            logger.debug(CMD_TEMPLATE)   
            logger.debug("Box create command: " + str(CMD))
        
            # 
            command_name = 'createcover'
            
            # Run Command
            
            if noexec:
                command[command_name] = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                logger.info("Running Command - " + str(command_name))  
                command[command_name] = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
                logger.info( "COMMAND " + command_name + " for "+ edgeid + " Started" )
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
                    logger.error("Error Message: " + str(stdoutdata))
                    logger.error("Error Message: " + str(stderrdata))
                    Error = True

                logger.info("Removing PSD files " + REMOVE_PSD)
                try:
                    if os.path.isfile (BOX_PSD):
                        logger.warn("File Exists " + str(REMOVE_PSD))
                    else:
                        logger.warn("File not found " + str(REMOVE_PSD))
                        for x in os.listdir(finaldestination):
                            print x
                                    
                    os.remove(REMOVE_PSD)
                except Exception, e:
                    print "Exception" + str(e)




if __name__ == "__main__":
    if DEBUG:
        print"DEBUG ON"
    if TESTRUN: 
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'generic_boxcover_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
   
    sys.exit(main())