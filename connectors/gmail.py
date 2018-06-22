"""
Shows basic usage of the Gmail API.

Lists the user's Gmail labels.
"""
from __future__ import print_function
from googleapiclient.discovery import build
from googleapiclient import discovery
import httplib2
from oauth2client import file, client, tools
from apiclient import errors
import re
import os

from common import logger

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'

def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,CLIENT_SECRET_FILE)

    store = file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = "WaitingList"
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def connect():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    return service


def gmail_get_emails(service,options):

    try:
        # Setup the Gmail API
        # SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
        # store = file.Storage('credentials.json')
        # creds = store.get()
        # if not creds or creds.invalid:
        #     flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        #     creds = tools.run_flow(flow, store)
        # service = build('gmail', 'v1', http=creds.authorize(Http()))



        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        # if not labels:
        #     print('No labels found.')
        # else:
        #     print('Labels:')
        #     for label in labels:
        #         print(label['name'])

        threads = service.users().threads().list(userId='me',maxResults=options.max_emails).execute().get('threads', [])
        # Check emails from MSG, and try to find a new mail with Wodify waiting list information into it.
        subject = ''

        for thread in threads:
            tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
            nmsgs = len(tdata['messages'])

            msg = tdata['messages'][0]['payload']
            msg_id = tdata['messages'][0]['id']
            for header in msg['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break


            if subject:
                logger.log('Message subject : %s' % (subject),"DEBUG",options)

            subject_wod = re.search("(?P<msg>The WOD : (.....) class is open for reservation)", subject)

            if subject_wod:
                subject_wod = subject_wod.group("msg")
                logger.log('Found WOD mail',"INFO",options)

                tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
                wod_msg = GetMessage(service,'me',msg_id)
                return wod_msg


            # No message found at this stage.
        return ''

    except errors.Error, error:
        print('An error occurred: %s' % error)



def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,format='raw').execute()

    #print('Message snippet: %s' % message['snippet'])

    return message
  except errors.HttpError, error:
    print('An error occurred: %s' % error)



def TrashMessage(service,msg_id):
  """Remove a  Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:

    print('Try to remove message with id :%s' % msg_id)
    message = service.users().messages().trash(userId='me', id=msg_id).execute()
    #print('Message snippet: %s' % message['snippet'])

    #return message
  except errors.HttpError, error:
    print('An error occurred when trying to delete message: %s' % error)

