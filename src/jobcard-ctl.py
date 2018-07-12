#!/usr/bin/env python3
 
__author__ = 'Colin Bitterfield'
__version__ = '1.0'
__programname__ = 'Jobcard Controller'
__createdate__ = '2018-07-14'
__builddate__ = '2018-07-14' 
 
PIDFILE = '/tmp/jobcard.pid'
LOGFILE = '/tmp/jobcard.log'
DELAY = 900 # Wait 15 minutes before checking again 
NUMTHREADS = 4 # Allow 4 jobcards to run at the same time. 
JOBDIR = "/edge/JobQueue/jobs"
JOBERR = "/edge/JobQueue/errors"
JOBLOG = "/edge/JobQueue/log"
 
import sys, time, os, datetime
from jobcard_daemon import daemon
 
class MyDaemon(daemon):
        def run(self):
            try:
                print('starting' + str(__programname__) + " version" + str(__version__))
                if os.path.isfile(LOGFILE):
                    log = open(LOGFILE,'a')
                else:
                    log = open(LOGFILE,'w')
                log.write('Starting services\n')  
            except Exception as e:
                print (e)
#===============================================================
# Run this code until the daemon is stopped
#===============================================================
            while True:
                now = datetime.datetime.now()
                if os.path.isfile(LOGFILE):
                    log = open(LOGFILE,'a')
                else:
                    log = open(LOGFILE,'w')              
                log.write('Checking for new work' + str(now) + '\n')
                
                # Destermine how many jobs are currently running
                locklist = os.listdir(JOBDIR)
                for filename in locklist:
                    logger.info(filename)
                
                # Start code for job card running here.
                time.sleep(DELAY)
                
 
 
 
if __name__ == "__main__":
        daemon = MyDaemon(PIDFILE)
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print ("Unknown command")
                        sys.exit(2)
                sys.exit(0)
        else:
                print ("usage: %s start|stop|restart" % sys.argv[0])
                sys.exit(2)
