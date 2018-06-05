"""
Shows basic usage of the Gmail API.

Lists the user's Gmail labels.
"""
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
import re


def gmail_get_emails(maxresults):

    # Setup the Gmail API
    SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    # if not labels:
    #     print('No labels found.')
    # else:
    #     print('Labels:')
    #     for label in labels:
    #         print(label['name'])

    threads = service.users().threads().list(userId='me',maxResults=maxresults).execute().get('threads', [])
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
            print('Message subject : %s' % (subject))

        subject_wod = re.search("(?P<msg>The WOD : (.....) class is open for reservation)", subject)

        if subject_wod:
            subject_wod = subject_wod.group("msg")
            print('Found WOD mail')

            tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
            wod_msg = GetMessage(service,'me',msg_id)
            return wod_msg


        # No message found at this stage.
    return ''




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