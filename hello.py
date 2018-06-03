"""
Shows basic usage of the Gmail API.

Lists the user's Gmail labels.
"""
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Gmail API
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

# Call the Gmail API
results = service.users().labels().list(userId='me').execute()
labels = results.get('labels', [])
if not labels:
    print('No labels found.')
else:
    print('Labels:')
    for label in labels:
        print(label['name'])

threads = service.users().threads().list(userId='me',maxResults=10).execute().get('threads', [])
for thread in threads:
    tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
    nmsgs = len(tdata['messages'])
    print(nmsgs)

    msg = tdata['messages'][0]['payload']
    subject = ''
    for header in msg['headers']:
        if header['name'] == 'Subject':
            subject = header['value']
            break
    if subject:
        print('%s (%d msgs)' % (subject, nmsgs))

