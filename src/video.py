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
import logging
logger = logging.getLogger(__name__)

# Additional Libraries
from string import Template
import task
import subprocess
import maketext
import time
import datetime





def produce(dest_vol, object, jobcard, config, volume, noexec):
    Error = False
    #===========================================================================
    # split object
    #===========================================================================
    
    try:
        object_name, object_number = object.split(".")
    except:
        object_name = object
        object_number = "0"
    #===========================================================================
    # Define Programs needed
    #===========================================================================
    CONVERT=config['programs']['convert']
    FFMPEG=config['programs']['ffmpeg']
    FFPROBE=config['programs']['ffprobe']
    MOGRIFY=config['programs']['mogrify']
    ATOMICPARSLEY = config['programs']['atomicparsley']
    
    
    
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
        item_suffix = jobcard[object]['suffix'] + str(object_number) if 'suffix' in jobcard[object] else "_" + str(object_number)
        item_ext = jobcard[object]['ext'] if 'ext' in jobcard[object] else None
        item_width = jobcard[object]['set_width'] if 'set_width' in jobcard[object] else None
        item_height = jobcard[object]['set_height'] if 'set_height' in jobcard[object] else None
        item_kbps = jobcard[object]['set_kbps'] if 'set_kbps' in jobcard[object] else None
        boxcover_action = jobcard['boxcover']['action'] if "action" in jobcard['boxcover'] else None
        if boxcover_action == 'produce' or boxcover_action == 'exists':
                try:
                    boxcover_name = jobcard['boxcover']['name'] if "name" in jobcard['boxcover'] else ""
                    boxcover_dir = jobcard['boxcover']['dir'] if "dir" in jobcard['boxcover'] else ""
                    boxcover_ext = jobcard['boxcover']['ext'] if "ext" in jobcard['boxcover'] else ""
                    # Eventually need to add code to derive different box covers.
                    logger.debug("This version of code only supports one boxcover")
                    boxcover_suffix = jobcard['boxcover']['suffix'] + str('0') if "suffix" in jobcard['boxcover'] else ""
                    
                except Exception as e: 
                    logger.error("Boxcover values are not properly set, please correct error " + str(e))
                    Error = True
                
        
        
    except Exception as e: 
        logger.error("Item values are not properly set, please correct error " + str(e))
        Error = True

    #===========================================================================
    # Get Codec Information
    #===========================================================================
    try:
        mp4_decode = config['codec']['mp4_decode'] if "mp4_decode" in config['codec'] else "h264"
        mp4_encode = config['codec']['mp4_encode'] if "mp4_encode" in config['codec'] else "h264"
        mp4_simple = config['codec']['mp4_simple'] if "mp4_simple" in config['codec'] else "mpeg4"
        mp4_jpeg = config['codec']['mp4_jpeg'] if "mp4_jpeg" in config['codec'] else "mjpeg"
        mp4_accel = config['codec']['mp4_accel'] if "mp4_accel" in config['codec'] else '-hwaccel videotoolbox'
        mp4_threads = config['codec']['mp4_threads'] if "mp4_threads" in config['codec'] else "-threads 8"
        mp4_scalefilter = config['codec']['mp4_scalefilter'] if "mp4_scalefilter" in config['codec'] else "-scale"
        
        
    except Exception as e: 
        logger.error("Codec values are not properly set, please correct error " + str(e))
        Error = True        
    
    video_scale = str(item_width) + ":" + str(item_height)
    video_bufsize = int(str(item_kbps)) * 1000
    
    #===========================================================================
    # Load Preview and Compliance Parameters
    #===========================================================================
    try:
                
        intro_color = config['intro']['intro_color'] if 'intro_color' in config['intro'] else 'black'
        intro_font_color = config['intro']['intro_font_color'] if 'intro_font_color' in config['intro'] else 'DarkMagenta'
        intro_back = config['intro']['intro_color'] if 'intro_color' in config['intro'] else 'blue'
        intro_font = config['intro']['intro_font'] if 'intro_font' in config['intro'] else '/usr/local/etc/Arial.ttf'
        intro_x = config['intro']['intro_x'] if 'intro_x' in config['intro'] else 100
        intro_y = config['intro']['intro_y'] if 'intro_y'  in config['intro'] else 100
        intro_fontsize = config['intro']['intro_font_size'] if 'intro_font_size' in config['intro'] else 50
        intro_suffix = config['intro']['intro_suffix'] + str(object_number) if 'intro_suffix' in config['intro'] else '_intro'
        intro_ext = config['intro']['intro_ext'] if 'intro_ext' in config['intro'] else '.mp4'
        intro_title_font_size = config['intro']['intro_title_font_size'] if 'intro_title_font_size' in config['intro'] else 80
        intro_short_font_size = config['intro']['intro_short_font_size'] if 'intro_short_font_size' in config['intro'] else 80
        # Remember to look for absolute
        compliance_template = config['compliance']['template'] if 'template' in config['compliance'] else None
        compliance_back = config['compliance']['compliance_color'] if 'compliance_color' in config['compliance'] else 'black'
        compliance_color = config['compliance']['compliance_text_color'] if 'compliance_text_color' in config['compliance'] else 'green' 
        compliance_textsize = config['compliance']['compliance_text_size'] if 'compliance_text_size' in config['compliance'] else 50
        compliance_suffix = config['compliance']['compliance_suffix'] + str(object_number) if 'compliance_suffix' in config['compliance'] else '_preview'
        compliance_ext = config['compliance']['compliance_ext'] if 'compliance_ext' in config['compliance'] else '.mp4'
        compliance_font = config['compliance']['compliance_font'] if 'compliance_font' in config['compliance'] else '/usr/local/etc/Arial.ttf'
        compliance_fontsize = config['compliance']['compliance_font_size'] if 'compliance_font_size' in config['compliance'] else 50
    
    except Exception as e: 
        logger.error("Preview and Compliance values are not properly set, please correct error " + str(e))
        Error = True   
    
    #===========================================================================
    # Load minimal compliance information
    # If the file is missing; then we will generate a new one
    #===========================================================================
    logger.debug("Set Compliance key value pairs")
    try:
        compliance_name = jobcard['text.compliance']['name'] if 'name' in jobcard['text.compliance'] else None
        compliance_dir = jobcard['text.compliance']['dir'] if 'dir' in jobcard['text.compliance'] else None
        compliance_suffix = jobcard['text.compliance']['suffix'] if 'suffix' in jobcard['text.compliance'] else None
        compliance_ext = jobcard['text.compliance']['ext'] if 'ext' in jobcard['text.compliance'] else None
        video_compliance_suffix = config['compliance']['compliance_suffix'] if 'compliance_suffix' in config['compliance'] else "_video_compliance"
    
    except Exception as e: 
        logger.error("Compliance values are not properly set, please correct error " + str(e))
        Error = True
    
    logger.debug("Compliance Suffix: " + str(compliance_suffix))
    
    #===========================================================================
    # Get Clip Info needed
    #===========================================================================
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
        clip_star2 = True if "star2" in jobcard['clipinfo'] else False
        if clip_star2:
            logger.info("Loading Star 2")
            clip_star2_name = jobcard['clipinfo']['star2']['name'] if "name" in jobcard['clipinfo']['star2'] else ''
        clip_supporting_name = jobcard['clipinfo']['supporting']['name'] if "name" in jobcard['clipinfo']['supporting'] else ''
        clip_description = jobcard['clipinfo']['description'] if "description" in jobcard['clipinfo'] else ""
        clip_licensor = jobcard['clipinfo']['licensor'] if "licensor" in jobcard['clipinfo'] else ""
        clip_productiondate = jobcard['clipinfo']['productiondate']
              
        
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
    # Clean up the title and short title for apostophes
    # Set up proper padding for Star and or Star2
    # Resize source image
    #===========================================================================
    
    f_clip_title = clip_title.replace("'","\\'")
    f_clip_shorttitle = clip_shorttitle.replace(" ","\\n")
    
    #===========================================================================
    # Load suffix for intermediary steps
    #===========================================================================
    try:
        transcode_suffix = config['video']['transcode_suffix'] + str(object_number) if "transcode_suffix" in config['video'] else "_transcode"
        assembly_suffix = config['video']['assembly_suffix']  + str(object_number) if "assembly_suffix" in config['video'] else "_assembly"

  
    except Exception as e:  
        logger.warning("Not all suffix variables set properly; exception " + str(e)) 
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
        
        
    #===========================================================================
    # If there is a boxcover, we need to figure out where it is
    #===========================================================================
    if not boxcover_name == None and not boxcover_name == None:
        boxcoverdestination = destination + "/" + str(boxcover_name) + "/" + str(boxcover_dir)
    elif not boxcover_name == None and boxcover_dir == None:
        boxcoverdestination = destination + "/" + str(boxcover_name)
    elif compliance_name == None and not boxcover_dir == None:
        boxcoverdestination = destination + "/" + str(boxcover_dir)     
    else:
        boxcoverdestination = destination
    
    boxcoverename = edgeid + boxcover_suffix + boxcover_ext
    
    
    
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
    # Test for Complaince file
    #===========================================================================
    #setup final destination in compliance 
    logger.debug("Check for Compliance file")
    if not compliance_name == None and not compliance_dir == None:
        compliancedestination = destination + "/" + str(compliance_name) + "/" + str(compliance_dir)
    elif not compliance_name == None and compliance_dir == None:
        compliancedestination = destination + "/" + str(compliance_name)
    elif compliance_name == None and not compliance_dir == None:
        compliancedestination = destination + "/" + str(compliance_dir)     
    else:
        compliancedestination = destination
    
    compliancename = edgeid + compliance_suffix + compliance_ext
    
    if os.path.isfile(str(compliancedestination) + "/" + str(compliancename)):
        logger.debug("Compliance file exists")
    
    else:
        logger.debug("Compliance file is missing, program will create one")
        Error = maketext.produce(dest_vol,'text.compliance', jobcard, config, volume, noexec)
        
    
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
    # Look for watermark and thumbnail variables
    #===========================================================================
    if item_watermark:
        logger.warn("This version does not support watermarking")
    
    if item_thumbnail:
        logger.warn("This version does not thumbnail creation")
   
    #===========================================================================
    # Phase 1: Get Video Parameters and Generate a MD5 hash
    #===========================================================================
    logger.debug("Phase 1: Get Video Parameters and Generate a MD5 hash")
    video_md5 = task.md5(item_source,noexec)
    
    Error, height, width, duration, bitrate = task.videosize(item_source, config, noexec)
    logger.info("[" + str(item_source) + " " + str(width) + "x" + str(height) + "x" + str(bitrate) + " kbps " + "duration: " + str(duration) + " MD5: " + video_md5)
    
    #===========================================================================
    # Phase 2: Transcode Video
    #===========================================================================
    logger.debug("Phase 2: Transcode Video " + str(item_source))
    

    # Note: Temporarily turn off watermarking
    item_watermark = False
       
    if item_watermark == False:
        CMD_TEMPLATE = "$FFMPEG  -threads 64  $MP4_ACCEL  -c:v $DECODEC -y -i '$VIDEO'  -vf $SCALEFILTER=$SCALE,setdar=dar=16/9  -b:v ${KBPS}k -maxrate ${KBPS}k -bufsize $BUFSIZE  -preset fast  -c:v $ENCODEC '$DESTINATION/${EDGEID}_${WIDTH}x${HEIGHT}x${KBPS}${SUFFIX}${EXT}'"
        watermark = ""
    else:
        logger.info("Watermarking the video" + str(watermark.encode('utf-8')))
        CMD_TEMPLATE = "$FFMPEG  -threads 64  $MP4_ACCEL  -c:v $DECODEC -y -i '$VIDEO' -vf $WATERMARK -vf $SCALEFILTER=$SCALE,setdar=dar=16/9  -b:v ${KBPS}k -maxrate ${KBPS}k -bufsize $BUFSIZE  -preset fast  -c:v $ENCODEC '$DESTINATION/${EDGEID}_${WIDTH}x${HEIGHT}x${KBPS}${SUFFIX}${EXT}'"
    
    CMD = Template(CMD_TEMPLATE).safe_substitute(FFMPEG=FFMPEG,HWACCEL=mp4_accel, WATERMARK=str(watermark.encode('utf-8')), VIDEO=item_source, DECODEC=mp4_decode, ENCODEC=mp4_encode,MP4_ACCEL=mp4_accel, SCALEFILTER=mp4_scalefilter, SCALE=video_scale, HEIGHT=item_height, WIDTH=item_width, KBPS=item_kbps, BUFSIZE=video_bufsize, DESTINATION=finaldestination, EDGEID=edgeid, SUFFIX=transcode_suffix, EXT=item_ext)

    logger.warning("Transcode Command " + CMD)
    if  noexec:
        transcode_result = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logger.warning("Running Command" )  
        transcode_result = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
        logger.info( "Transcode" + item_src + " Started" )

    #===============================================================================
    # Phase 3: Generate introduction video
    #===============================================================================
    logger.debug("Phase 3: Generate introduction video")
    if clip_star2:
        all_star = clip_star_name + " & " + clip_star2_name
    else:
        all_star = clip_star_name
    
    logger.debug("All Star: " + str(all_star))
    logger.debug("Supporting: " + str(clip_supporting_name))
    logger.debug("Title: " + str(f_clip_title))
    logger.debug("Short Title: " + str(f_clip_shorttitle))
    logger.debug("EdgeID: " + str(edgeid))



    logger.debug("Creating Preview for " + object)
    
    logger.debug("Creating Preview for " + object)
    
    CMD = FFMPEG + " -y -f lavfi -r 29.97 -i color=" + intro_color +":"+ str(item_width) + "x" + str(item_height) + " -f lavfi -i anullsrc -filter_complex  "
    # Make Title Line
    CMD = CMD + "\"fade=t=in:st=00:d=0.5,fade=t=out:st=04:d=1,drawtext=enable='between(t,.5,04)':fontfile=" + intro_font_color + ":text=\'" + f_clip_title + " " + edgeid+  "\':x=(w-text_w)/2" + ":y=" + str(intro_y) +":fontcolor=" + intro_font_color  + ":fontsize=" + str(intro_title_font_size)
    # Sub Title
    CMD = CMD +  ",drawtext=enable='between(t,.5,04)':fontfile=" + intro_font + ":text=\'Starring " + "\':x=(w-text_w)/2" +":y=" + str(intro_y+100) +":fontcolor=" + intro_font_color + ":fontsize=" + str(intro_fontsize)
    
    CMD = CMD +  ",drawtext=enable='between(t,.5,04)':fontfile=" + intro_font + ":text=\'" + all_star + " with " + clip_supporting_name + "\':x=(w-text_w)/2" +":y=" + str(intro_y+200) +":fontcolor=" + intro_font_color + ":fontsize=" + str(intro_fontsize)
    
    CMD = CMD +  ",drawtext=enable='between(t,.5,04)':fontfile=" + intro_font + ":text=\'IN " + "\':x=(w-text_w)/2" +":y=" + str(intro_y+300) +":fontcolor=" + intro_font_color + ":fontsize=" + str(intro_fontsize)
    
    # Keywords
    CMD = CMD +  ",drawtext=enable='between(t,.5,04)':fontfile=" + intro_font + ":text=\'" + clip_shorttitle + "\':x=(w-text_w)/2:y=" + str(intro_y+400) +":fontcolor=" + intro_font_color + ":fontsize=" + str(intro_short_font_size)
    
    CMD = CMD +  ",drawtext=enable='between(t,.5,04)':fontfile=" + intro_font + ":text=\'Release Date " + jobcard['clipinfo']['releasedate'] + "\':x=(w-text_w)/2:y=" + str(intro_y+500) +":fontcolor=" + intro_color + ":fontsize=" + str(intro_fontsize*.6)
    CMD = CMD +  ",drawtext=enable='between(t,.5,04)':fontfile=" + intro_font + ":text=\'Production Date " + jobcard['clipinfo']['productiondate'] + "\':x=(w-text_w)/2:y=" + str(intro_y+550) +":fontcolor=" + intro_color + ":fontsize=" + str(intro_fontsize*.6)

    # Wrap end of command
    CMD = CMD + "\" -c:v " + mp4_simple + " -b:v " + str(item_kbps) + "k -pix_fmt yuv420p -video_track_timescale 15360 -c:a aac -strict -2 -ar 48000 -ac 2 -sample_fmt fltp -t 05 '" + finaldestination + "/" + edgeid + "_" + str(item_width) + "x" + str(item_height) + "x" + str(item_kbps) + str(intro_suffix) + str(intro_ext) +"'" 

    logger.info("Preview Command: " + str(CMD))
    if noexec:
        preview_result = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logger.warning("Running Command" )  
        preview_result = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
        logger.info( "Preview" + item_src + " Started" )

    #===========================================================================
    # Phase 4: Generate compliance video
    #===========================================================================
    logger.debug("Phase 4: Generate compliance video")
    
    #Normalize the text size based on 1920x1080
    normalize = float(float(item_height) / float(1080))
    logger.info("Normalize the size by " + str(normalize))
    normalized_font = int(float(compliance_textsize) * normalize)
    logger.info("Normalized size " + str(normalized_font))
    
    logger.info("Text File Location:" + compliancedestination + "/" + edgeid + compliance_suffix + compliance_ext )
    CMD = FFMPEG + " -y -f lavfi -r 29.97 -i color=" + compliance_back + ":" +str(item_width) + "x" + str(item_height) + " -f lavfi -i anullsrc -vf drawtext=\"fontfile=" + compliance_font + ":fontcolor=" + compliance_color + ": fontsize=" + str(normalized_font) + ":textfile='" + compliancedestination  + "/" + edgeid + compliance_suffix + compliance_ext + "'" + ":x=50:y=50,fade=t=in:st=00:d=3.5,fade=t=out:st=08:d=2\" -c:v mpeg4 -b:v " + str(item_kbps) + "k  -pix_fmt yuv420p -video_track_timescale 15360 -c:a aac -strict -2 -ar 48000 -ac 2 -sample_fmt fltp -t 10 '" + finaldestination + "/" + edgeid + "_" + str(item_width) + "x" + str(item_height) + "x" + str(item_kbps) + video_compliance_suffix + item_ext + "'"

    logger.info("Compliance Command: " + str(CMD))
    if noexec:
        compliance_result = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logger.warning("Running Command" )  
        compliance_result = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
        logger.info( "Compliance" + item_src + " Started" )

    


    #===========================================================================
    # Phase 5: Wait for transcode, preview and compliance to complete
    #===========================================================================
    logger.debug("Phase 5: Wait for transcode, preview and compliance to complete")
    logger.info("Check if Preview Completed")
    stdoutdata, stderrdata = preview_result.communicate()
    preview_status = preview_result.returncode 
    if preview_status == 0:
        logger.info("Preview Completed, returned Status: " + str(preview_status))
    else:
        logger.error("Preview failed, with Status:"+ str(preview_status))
        Error = True

    logger.info("Check if Compliance Completed")
    stdoutdata, stderrdata = compliance_result.communicate()
    compliance_status = compliance_result.returncode 
    if compliance_status == 0:
        logger.info("Compliance Completed, returned Status: " + str(compliance_status))
    else:
        logger.error("Compliance failed, with Status:"+ str(compliance_status))
        Error = True

    logger.info("Check if Transcode Completed")
    stdoutdata, stderrdata = transcode_result.communicate()
    transcode_status = transcode_result.returncode 
    if transcode_status == 0:
        logger.info("Transcode returned Status: " + str(transcode_status))
    else:
        logger.error("Transcode failed with Status:"+ str(transcode_status))
        Error = True
    
    #===========================================================================
    # Phase 6: Concat the Preview - Transcode - Compliance Videos
    #===========================================================================
    logger.debug("Phase 6: Concat the Preview - Transcode - Compliance Videos")
    CMD = FFMPEG + "  -i '" + finaldestination + "/" + edgeid + "_" + str(item_width) + "x" + str(item_height) + "x" + str(item_kbps) + intro_suffix + intro_ext + "'  -i '" + finaldestination + "/" + edgeid + "_" + str(item_width) + "x" + str(item_height) + "x" + str(item_kbps) + str(transcode_suffix) + item_ext + "' -i '"  + finaldestination + "/" + edgeid + "_" + str(item_width) + "x" + str(item_height) + "x" + str(item_kbps)  + video_compliance_suffix + item_ext + "' " 
    CMD = CMD + "-filter_complex 'concat=n=3:v=1:a=1'  -c:v " + mp4_encode +" -b:v " + str(item_kbps) +"k -bufsize 1500000  -c:a aac -strict -2  -y '"   + finaldestination + "/" + edgeid + "_" + str(item_width) + "x" + str(item_height) + "x" + str(item_kbps) + str(assembly_suffix) + str(item_ext)  + "'"
 
    logger.warning("Concat Command\n\t" + CMD)
    if not noexec:
        concat_result = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("Check if Concat Completed")
        stdoutdata, stderrdata = concat_result.communicate()
        concat_status = concat_result.returncode 
        if concat_status == 0:
            logger.info("Concat returned Status: " + str(concat_status))
        else:
            logger.error("Concat failed with Status:"+ str(concat_status))
            Error = True
    else:
        concat_result = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    
    
    
    #===========================================================================
    # Phase 7: Add Meta Data to MP4 Video
    #===========================================================================
    logger.debug("Phase 7: Add Meta Data to MP4 Video")
    source_video = finaldestination + "/" + edgeid + "_" + str(item_width) + "x" + str(item_height) + "x" + str(item_kbps) + str(assembly_suffix) + str(item_ext)
    logger.info("Adding Meta data to " + str(source_video))
    
    #===========================================================================
    # Derive UTC from date the easy way
    #===========================================================================
    timestamp = time.mktime(datetime.datetime.strptime(clip_productiondate, "%B %d, %Y").timetuple())
    utc_production_date = str(datetime.datetime.utcfromtimestamp(int(timestamp)))
    
    # Create Metadata
    quote = "\""

    artist = quote + str(all_star) + quote
    title = quote + clip_title + " " + edgeid + quote
    album = quote + edgeid + quote
    genre = quote + "adult" + quote
    comment = quote + "myComment" + quote
    year = quote + str(utc_production_date) + quote
    composer = quote + clip_licensor + quote
    copyright_text = quote + "This Product copyright 2017 Edge Interactive Publishing, New York. You are granted the right to view and store this Product for your personal use only. It is violation of copyright law to duplicate in whole or in part this Product for other than your own personal use and storage. No right is granted for reproduction of these images for gifting, licensing, or resale. This Product is not available for sale in any store. Because of the sexual nature of this Product it is also a violation of Federal Criminal Code to distribute this Product unless you hold the appropriate proofs of identity and age of the performers at the time of this shoot. " + quote
    grouping = quote + clip_prime_dubya + quote
    artwork = quote + boxcoverdestination + "/" + boxcoverename + quote
    albumArtist = quote + all_star + quote 
    advisory = quote + "explict" + quote
    stik = quote + "Movie" + quote
    description = quote + clip_description + quote
    TVNetwork = quote + "Edge Interactive Media" + quote
    TVShowName = quote + clip_shorttitle + quote
    TVEpisode = quote + edgeid + quote
    TVSeasonNum = quote  + "01" + quote
    TVEpisodeNum = quote + "00" + quote
    category = quote + "adult" + quote
    keyword = quote  + clip_keywords + quote
    encodingTool = quote + mp4_encode + quote
    
    meta_video =  edgeid + "_" + str(item_width) + "x" + str(item_height) + "x" + str(item_kbps) + str(item_suffix) + str(item_ext)
    
        
    CMD = ATOMICPARSLEY + " '" + source_video + "' " 
    CMD = CMD + " --artist " + str(artist)
    CMD = CMD + " --title " + str(title)
    CMD = CMD + " --album " + str(album)
    CMD = CMD + " --genre " + str(genre)
    CMD = CMD + " --comment " + str(comment)
    CMD = CMD + " --year " + str(year)
    CMD = CMD + " --composer " + str(composer) 
    CMD = CMD + " --copyright " + str(copyright_text)
    CMD = CMD + " --grouping " + str(grouping)
    CMD = CMD + " --albumArtist " + str(albumArtist)
    CMD = CMD + " --advisory  " + str(advisory)
    CMD = CMD + " --stik " + str(stik)
    CMD = CMD + " --description " + str(description)
    CMD = CMD + " --TVNetwork " + str(TVNetwork)
    CMD = CMD + " --TVShowName " + str(TVShowName)
    CMD = CMD + " --TVEpisode " + str(TVEpisode)
    CMD = CMD + " --TVSeasonNum " + str(TVSeasonNum)
    CMD = CMD + " --TVEpisodeNum " + str(TVEpisodeNum)
    CMD = CMD + " --category " + str(category)
    CMD = CMD + " --keyword  " + str(keyword)
    CMD = CMD + " --encodingTool " + str(encodingTool)
    
    

    if boxcover_action == "produce" or boxcover_action == "exists":
        CMD = CMD + " --artwork " + str(artwork)
    else:
        logger.debug("No artwork available") 
        # Eventually add generic art here

    CMD = CMD + " --output '" + finaldestination + "/" + meta_video + "'"

    logger.warning("Metadata Command\n\t" + CMD)
    if noexec:
        metadata_result = subprocess.Popen("echo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logger.warning("Adding Metadata to temporary video" )  
        metadata_result = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
        logger.info( "Metadata" + item_src + " Started" )  
        logger.info("Check if Metadata adding has Completed") 
        stdoutdata, stderrdata = metadata_result.communicate()
        meta_status = metadata_result.returncode
        if meta_status == 0:
            logger.info("\t\Metadata add returned Status: " + str(meta_status))
        else:
            logger.error("\t\tMetadata add failed with Status:"+ str(meta_status))
            Error = True
    #===========================================================================
    # Clean up temporary files
    #===========================================================================
        # Delete the temporary use assembled video
    if True:
        #Validate the final video exists first
        logger.info("temp assembly video: " + str(source_video))
        if not os.path.isfile(source_video):
            logger.warn("Temp video does not exist")
        else:
            if os.path.isfile(finaldestination + "/" + meta_video) and os.path.isfile(source_video):
                logger.info("Final Video is there we can")
                logger.info("Removing temporary video: " + source_video)
                os.remove(source_video)
            else:
                logger.error("Final Video is missing " + str(finaldestination) + "/" + str(meta_video))
                logger.error("intermediate video will not be removed")
    
    
    
    
    
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