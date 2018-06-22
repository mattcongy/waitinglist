from common import logger

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

def parse(msg,options):

    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    mime_msg = email.message_from_string(msg_str)

    WM = WodifyMessage()
    # Parse Date, Program, Location and Start Time.

    print(WM.date)
    b = mime_msg
    if b.is_multipart():
        # Take first payload for the moment.

        payload = b.get_payload()[1]

        logger.log("%s, %s" % (payload.get_content_type(), payload.get_content_charset()),"DEBUG",options)

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
        logger.log(payload_str,"DEBUG",options)


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

        logger.log(print_WM(WM),"DEBUG",options)

        return WM


    else:
        logger.log(b.get_payload(),"DEBUG",options)

    #print(mime_msg)
    return msg



def print_WM(WMObject):
    return("Date : %s\nStartTime: %s\nProgram: %s\nLocation: %s\nName: %s\nAcceptURL: %s" % (WMObject.date, WMObject.startTime,WMObject.program,WMObject.location,WMObject.name,WMObject.acceptURL))


def decode_unicode(str):
    if str:
        return str.replace('=C2=A0','').replace('=3D','=')


def accept_waitingList(WMObject,options):

    returnCode=1

    response = urllib2.urlopen(WMObject.acceptURL)
    html_response = response.read()

    # Parse into HTML if the accept url succeed, if we are in !
    soup = BeautifulSoup(html_response,"html.parser")

    for divs in soup.find_all('div'):
        if "Class Reservation Not Found" in divs.text:

            logger.log("Class Reservation not found, unable to fill the queue...","INFO",options)
            returnCode = 1
            break
        elif "Sweet" in divs.text:
            logger.log("Filling the queue. It is ok ! ","INFO",options)
            returnCode = 0
            break


    return returnCode


