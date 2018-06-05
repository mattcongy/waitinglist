
import email
import base64
import re

import urllib2

from bs4 import BeautifulSoup

class WodifyMessage:
    name = ''
    date = ''
    location = ''
    acceptURL = ''
    startTime = ''
    program = ''

def parse(msg):

    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    mime_msg = email.message_from_string(msg_str)

    WM = WodifyMessage()
    # Parse Date, Program, Location and Start Time.

    print(WM.date)
    b = mime_msg
    if b.is_multipart():
        # Take first payload for the moment.

        payload = b.get_payload()[1]

        print "%s, %s" % (payload.get_content_type(), payload.get_content_charset())

        if payload.get_content_charset() is None:
            # We cannot know the character set, so return decoded "something"
            text = payload.get_payload(decode=True)

        charset = payload.get_content_charset()

        if payload.get_content_type() == 'text/plain':
            text = unicode(payload.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

        if payload.get_content_type() == 'text/html':
            html = unicode(payload.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

        # if payload.is_multipart(): ...
        payload_str = html

        # TODO : put in Verbose this print.
        #print(payload_str)

        soup = BeautifulSoup(payload_str)

        print("---------------------------")
        # Find Wod Information
        for div in soup.find_all('div'):
            if 'OSFillParent' in div.get('class'):
                print(div.text)
                WM.date = re.search("(Date):(.*-2018)",div.text).groups()[1]
                WM.startTime = re.search("(Start time:)((.*)(Program))",div.text).groups()[2]
                WM.program = re.search("(Program:)((.*)(Location))",div.text).groups()[2]
                WM.location = re.search("(Location:)((.*)(Name:))",div.text).groups()[2]
                WM.name = re.search("(Name:)((.*))",div.text).groups()[2]



        print("---------------------------")
        # Find accept link
        for link in soup.find_all('a'):
            if 'Accept' in link.string:
                WM.acceptURL = link.get('href')


        # TODO: Update in Debug mode this information
        print_WM(WM)

        return WM


    else:
        print b.get_payload()

    #print(mime_msg)
    return msg



def print_WM(WMObject):
    print("Date : %s\nStartTime: %s\nProgram: %s\nLocation: %s\nName: %s\nAcceptURL: %s" % (WMObject.date, WMObject.startTime,WMObject.program,WMObject.location,WMObject.name,WMObject.acceptURL))


def decode_unicode(str):
    if str:
        return str.replace('=C2=A0','').replace('=3D','=')


def accept_waitingList(WMObject):

    result=0

    response = urllib2.urlopen(WMObject.acceptURL)
    html_response = response.read()

    # Parse into HTML if the accept url succeed, if we are in !

    # TODO: Check if it is accepted or not.
    soup = BeautifulSoup(html_response)

    for divs in soup.find_all('div'):
        if "Class Reservation Not Found" in divs.text:
            print("Class Reservation not found, unable to fill the queue...")
            returnCode = 1
            break
        elif "Congratulations" in divs.text:
            print("Filling the queue. It is ok ! ")
            returnCode = 0
            break


    return returnCode


    return result

