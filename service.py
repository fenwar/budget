from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = "https://www.googleapis.com/auth/spreadsheets"
CREDENTIALS_FILE = "credentials.json"
CLIENT_SECRET_FILE = "client_secret.json"

def connect_to_api():
    """
    Load the credentials & get connected to the Google sheets API.

    Returns a googleapiclient.discovery.Resource which can be used to
    work with the user's spreadsheets.
    """
    store = file.Storage(CREDENTIALS_FILE)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build("sheets", "v4", http=creds.authorize(Http()))
    return service
