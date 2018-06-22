
from optparse import OptionParser
from connectors import gmail
from parsers import wodify
from threading import Thread
import time
import schedule

from common import logger




import sys

def SetupOptionParser():
    # Define all options available to the script.

    parser = OptionParser(usage=__doc__)
    parser.add_option('--check_interval',
                      default="60",
                      action='store',
                      dest='check_interval',
                      help='Intervals to check new email from Wodify in seconds. Default is 60')

    parser.add_option('--max_emails',
                      default="5",
                      action='store',
                      dest='max_emails',
                      help='Number of last email to check. Default is 10')

    parser.add_option('--verbose',
                      default="false",
                      action='store',
                      dest='verbose',
                      help='Launch the application in verbose mode.')

    return parser




def start_check(options):
    logger.log("Start Checking...","INFO",options)
    options_parser = SetupOptionParser()
    (options, args) = options_parser.parse_args()



    # Call the Gmail API
    service = gmail.connect()

    # Get emails
    msg = gmail.gmail_get_emails(service,options)

    if msg:
        logger.log("Message found, try to parse","DEBUG",options)
        wmobject = wodify.parse(msg,options)
        wodify.accept_waitingList(wmobject)
        gmail.TrashMessage(service,msg['id'])
    else:
        logger.log("No waiting list message found.","INFO",options)


    logger.log("End of checking...","INFO",options)
    return


def main(argv):
    # Keep argurments
    options_parser = SetupOptionParser()
    (options, arguments) = options_parser.parse_args()

    arg_max_emails = options.max_emails
    arg_check_interval = float(options.check_interval)

    logger.log("Launching WaitingList application !","INFO",options)
    logger.log("Verbose mode activated","DEBUG",options)

    schedule.every(arg_check_interval).seconds.do(start_check,options)

    while True:
        schedule.run_pending()
        time.sleep(1)




if __name__ == '__main__':
  main(sys.argv)