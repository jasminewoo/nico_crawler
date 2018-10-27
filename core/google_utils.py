import time

from googleapiclient.discovery import build
from httplib2 import Http, ServerNotFoundError
from oauth2client import file, client, tools

from core.path_utils import get_root_prefix


def create_service(api_name, api_version, scopes):
    prefix = get_root_prefix()
    store = file.Storage(prefix + '{}_{}_token.json'.format(api_name, api_version))
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(prefix + 'credentials.json', scopes)
        creds = tools.run_flow(flow, store)
    while True:
        try:
            return build(api_name, api_version, http=creds.authorize(Http()))
        except (ServerNotFoundError, TimeoutError):
            time.sleep(2)
