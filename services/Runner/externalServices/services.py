import util_log
import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
import json

# maximum number of retries to the service
MAX_RETRIES = 5


class Service():
    name = ""
    root = ""

    def is_online(self):
        """Check, if this service is already online"""
        try:
            requests.get(self.root)
            return True
        except Exception as e:
            util_log.error(e)
            return False


class API():
    def __init__(self, service, root, name, data_placeholder=None, method="POST"):
        self.service = service
        self.root = root
        self.name = name
        self.data_placeholder = data_placeholder
        self.method = method
        self.URL = "{0}/{1}".format(self.root, self.name)

    def callback(self, response):
        response.raise_for_status()
        return json.loads(response.text)

    def formatData(self, data):
        """format the data ready to be transmitted"""
        if not isinstance(data, list):
            raise Exception('Expecting parameter to be a list')
        if type(self.data_placeholder) is list:  # Support multiple params for API
            assert len(self.data_placeholder) == len(data)
            __data = {}
            for placeholder, val in zip(self.data_placeholder, data):
                __data[placeholder] = val
            return __data
        elif self.data_placeholder:
            return {self.data_placeholder: data}
        else:
            return {}

    def blocking_send(self, data=None):
        __data = self.formatData(data)
        for i in range(MAX_RETRIES):
            try:
                if self.method == "POST":
                    response = requests.post(self.URL, json=__data, timeout=3 * 60)
                else:
                    response = requests.get(self.URL, params=__data, timeout=3 * 60)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise RemoteException('Service {} returned an HTTP-Error ({}):\n{}'.format(self.service.name, response.status_code, response.text))
            except requests.exceptions.HTTPError as err:
                util_log.error("{0} is not yet ready!".format(self.URL))
                pass
            except requests.exceptions.ConnectionError as ex:
                util_log.error("Connection Refused: Make sure {0} is up.".format(self.service.name))
            except RemoteException as ex:
                # remote exceptions will directly be forwarded and we stop here
                raise ex
            except Exception as ex:
                util_log.error(ex)
                pass
        raise FailAfterRetries('Giving up after {} retries to reach {}() at {}.'.format(MAX_RETRIES, self.name, self.service.name))

    def send(self, data=None):
        __data = self.formatData(data)
        session = FuturesSession()
        futures = []
        for i in range(MAX_RETRIES):
            try:
                if self.method == "POST":
                    futures = [session.post(self.URL, json=__data)]
                else:
                    futures = [session.get(self.URL, params=__data)]

                for future in as_completed(futures):
                    resp = future.result()
                    if resp.status_code == 200:
                        return resp.json()
                    else:
                        raise RemoteException('Service {} returned an HTTP-Error ({}):\n{}'.format(self.service.name, resp.status_code, resp.text))

            except requests.exceptions.HTTPError as err:
                util_log.error("{0} is not yet ready!".format(self.URL))
                pass
            except requests.exceptions.ConnectionError as ex:
                util_log.error("Connection Refused: Make sure {0} is up.".format(self.name))
            except RemoteException as ex:
                # remote exceptions will directly be forwarded and we stop here
                raise ex
            except Exception as ex:
                util_log.error(ex)
                pass
        raise FailAfterRetries('Giving up after {} retries to reach {}() at {}.'.format(MAX_RETRIES, self.name, self.service.name))


class FailAfterRetries(Exception):
    """
    raised after multiple retries to a service failed
    """
    pass


class RemoteException(Exception):
    """
    raised after we receive an error from a remote service
    """
    pass
