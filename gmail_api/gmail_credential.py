import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_credential():
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "token.pickle")
    client_id_path = os.path.join(os.path.dirname(__file__), "client_id.json")
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_id_path, SCOPES)
            # creds = flow.run_local_server()
            creds = flow.run_console()
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    return creds
