import requests

from .auth import Auth


def check_request(resp):
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    except requests.exceptions.RequestException as err:
        print(err)
    return resp


class ApiClient(Auth):

    def __init__(self, server, export_url, userid, domain):
        super(ApiClient, self).__init__(server, userid)
        self.export_url = export_url
        self.domain = domain
        self.libns = self.get_export_url() + "components/library.owl#"
        self.dcdom = self.get_export_url() + "data/ontology.owl#"
        self.xsdns = "http://www.w3.org/2001/XMLSchema#"
        self.topcls = "http://www.wings-workflows.org/ontology/component.owl#Component"

    def get_request_url(self):
        return self.server + "/users/" + self.userid + "/" + self.domain + "/"

    def get_export_url(self):
        return self.export_url + "/export/users/" + self.userid + "/" + self.domain + "/"
