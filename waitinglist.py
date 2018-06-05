
from optparse import OptionParser
from connectors import gmail
from parsers import wodify


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
                      default="10",
                      action='store',
                      dest='max_emails',
                      help='Number of last email to check. Default is 10')


    return parser

def main(argv):
    options_parser = SetupOptionParser()
    (options, args) = options_parser.parse_args()

    # Get emails
    msg=gmail.gmail_get_emails(options.max_emails)

    if msg:
        wmobject = wodify.parse(msg)
        wodify.accept_waitingList(wmobject)
    else:
        print("No waiting list message found on your inbox")

    return

if __name__ == '__main__':
  main(sys.argv)