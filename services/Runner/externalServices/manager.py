import config
import json
import traceback
import requests

# maximum length of an error message to be stored
# excessive error messages might make it properly to the manager
MAX_ERROR_LENGTH = 2 * 1024 * 1024


class Manager_Service():

    root = config.manager_url

    def get_work(self):
        """retrieve a new work package from the manager node"""
        url = '{}/getWork'.format(self.root)
        resp = requests.post(
            url,
            params={'client': config.client_id},
            auth=requests.auth.HTTPBasicAuth(config.USER_NAME, config.USER_PASSWORD),
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            return None

    def get_desc(self, year, round, table):
        """
        retrieve a the package specified from the manager node
        this will not (!) assign the corresponding table to this client
        only meant for debug use
        """
        url = '{}/getDescription'.format(self.root)
        resp = requests.post(
            url,
            params={'year': year, 'round': round, 'table': table},
            auth=requests.auth.HTTPBasicAuth(config.USER_NAME, config.USER_PASSWORD),
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            return None

    def store_result(self, table, result):
        """store a result for the given table in the manager node"""
        url = '{}/storeResult/{}/'.format(self.root, table)
        resp = requests.put(
            url,
            params={'client': config.client_id},
            data=json.dumps(result),
            auth=requests.auth.HTTPBasicAuth(config.USER_NAME, config.USER_PASSWORD),
        )
        return resp.status_code == 200

    def store_error(self, table, errors=None):
        """store the last error for the given table in the manager node"""
        url = '{}/storeError/{}/'.format(self.root, table)

        # get error content
        trace = traceback.format_exc()

        # cut the error messages at a maximum length
        if len(trace) > MAX_ERROR_LENGTH:
            trace = trace[-MAX_ERROR_LENGTH:]

        # submit the error
        resp = requests.put(
            url,
            params={'client': config.client_id},
            data=trace.encode('utf-8'),
            auth=requests.auth.HTTPBasicAuth(config.USER_NAME, config.USER_PASSWORD),
        )
        return resp.status_code == 200

    def store_analysisData(self, table, data):
        """store analysis data the manager node"""
        url = '{}/storeAnalysisData/{}/'.format(self.root, table)
        resp = requests.put(
            url,
            params={'client': config.client_id},
            data=json.dumps(data),
            auth=requests.auth.HTTPBasicAuth(config.USER_NAME, config.USER_PASSWORD),
        )
        return resp.status_code == 200

    def audit_lst(self, records):
        """retrieve a new work package from the manager node"""
        url = '{}/audit_lst'.format(self.root)
        resp = requests.post(
            url,
            params={'client': config.client_id},
            data=json.dumps(records),
            auth=requests.auth.HTTPBasicAuth(config.USER_NAME, config.USER_PASSWORD),
        )
        return resp.status_code == 200


# create an instance for export
Manager = Manager_Service()
