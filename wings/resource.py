import json
import urllib
from .auth import Auth


class ManageResource(object):
    def __init__(self, api_client):
        self.api_client = api_client

    def get_machine(self, resid):
        params = {'resid': resid}
        resp = self.api_client.session.get(self.api_client.server + '/common/resources/getMachineJSON?' +
                                urllib.urlencode(params))
        return resp.json()

    def save_machine(self, mid, machine_data):
        params = {'resid': mid, 'json': json.dumps(machine_data)}
        self.api_client.session.post(
            self.api_client.server + '/common/resources/saveMachineJSON', params)