import json
import os
import re

import requests


class ManageData(object):

    def __init__(self, api_client):
        self.api_client = api_client

    def get_type_id(self, typeid):
        if typeid is None:
            return 'http://www.wings-workflows.org/ontology/data.owl#DataObject'
        elif not re.match(r"(http:|https:)//", typeid):
            return self.api_client.dcdom + typeid
        else:
            return typeid

    def get_data_id(self, dataid):
        if not re.match(r"(http:|https:)//", dataid):
            return self.api_client.dclib + dataid
        else:
            return dataid

    def new_data_type(self, dtype, parent):
        parent = self.get_type_id(parent)
        dtype = self.get_type_id(dtype)
        postdata = {'parent_type': parent, 'data_type': dtype}
        resp = self.api_client.session.post(self.api_client.get_request_url() +
                                            'data/newDataType', postdata)
        self.api_client.check_request(resp)
        return dtype

    def add_type_properties(self, dtype, properties):
        xsd = 'http://www.w3.org/2001/XMLSchema#'
        dtype = self.get_type_id(dtype)
        data = {'add': {}, 'del': {}, 'mod': {}}
        for pname in properties:
            pid = self.get_type_id(pname)
            prange = xsd + properties[pname]
            data['add'][pid] = {'prop': pname, 'pid': pid, 'range': prange}
        postdata = {'data_type': dtype, 'props_json': json.dumps(data)}
        self.api_client.session.post(self.api_client.get_request_url() +
                                     'data/saveDataTypeJSON', postdata)

    def add_data_for_type(self, dataid, dtype):
        dtype = self.get_type_id(dtype)
        dataid = self.get_data_id(dataid)
        postdata = {'data_id': dataid, 'data_type': dtype}
        resp = self.api_client.session.post(self.api_client.get_request_url() +
                                            'data/addDataForType', postdata)
        self.api_client.check_request(resp)

    def del_data_type(self, dtype):
        dtype = self.get_type_id(dtype)
        postdata = {'data_type': json.dumps([dtype]), 'del_children': 'true'}
        self.api_client.session.post(self.api_client.get_request_url() +
                                     'data/delDataTypes', postdata)

    def del_data(self, dataid):
        dataid = self.get_data_id(dataid)
        postdata = {'data_id': dataid}
        self.api_client.session.post(self.api_client.get_request_url() + 'data/delData', postdata)

    def get_all_items(self):
        resp = self.api_client.session.get(
            self.api_client.get_request_url() + 'data/getDataHierarchyJSON')
        return resp.json()

    def get_data_description(self, dataid):
        dataid = self.get_data_id(dataid)
        params = {'data_id': dataid}
        resp = self.api_client.session.get(
            self.api_client.get_request_url() + 'data/getDataJSON', params=params)
        return resp.json()

    def get_datatype_description(self, dtype):
        dtype = self.get_type_id(dtype)
        params = {'data_type': dtype}
        try:
            resp = self.api_client.session.get(
                self.api_client.get_request_url() + 'data/getDataTypeJSON', params=params)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        except requests.exceptions.RequestException as err:
            print(err)

    def upload_data_for_type(self, filepath, dtype):
        dtype = self.get_type_id(dtype)
        fname = os.path.basename(filepath)
        files = {'file': (fname, open(filepath, 'rb'))}
        postdata = {'name': fname, 'type': 'data'}
        response = self.api_client.session.post(self.api_client.get_request_url() + 'upload',
                                                data=postdata, files=files)
        if response.status_code == 200:
            details = response.json()
            if details['success']:
                dataid = os.path.basename(details['location'])
                dataid = re.sub(r"(^\d.+$)", r"_\1", dataid)
                self.add_data_for_type(dataid, dtype)
                self.set_data_location(dataid, details['location'])
                return dataid

    def save_metadata(self, dataid, metadata):
        pvals = []
        for key in metadata:
            if metadata[key]:
                pvals.append(
                    {'name': self.api_client.dcdom + key, 'value': metadata[key]})
        postdata = {'propvals_json': json.dumps(
            pvals), 'data_id': self.get_data_id(dataid)}
        resp = self.api_client.session.post(self.api_client.get_request_url() +
                                            'data/saveDataJSON', postdata)
        self.api_client.check_request(resp)

    def set_data_location(self, dataid, location):
        postdata = {'data_id': self.get_data_id(dataid), 'location': location}
        self.api_client.session.post(self.api_client.get_request_url() +
                                     'data/setDataLocation', postdata)
