from utils import util_log
import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
import json
import itertools

# maximum number of retries to the service
MAX_RETRIES = 5
# number of parameters send in a single query
QUERY_BATCH_SIZE = 250000


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
        """
        format the data ready to be transmitted
        data may be split into multiple requests, if it is too large
        """
        batches = []
        if type(self.data_placeholder) is list:  # Support multiple params for API
            assert len(self.data_placeholder) == len(data)

            # split all parameters into chunks, if necessary
            chunks = []
            for d in data:
                if isinstance(d, list):
                    chunks.append([d[i:i + QUERY_BATCH_SIZE] for i in range(0, len(d), QUERY_BATCH_SIZE)])
                else:
                    chunks.append([d])

            # add all combinations
            # https://stackoverflow.com/a/798893/1169798
            for comb in list(itertools.product(*chunks)):
                __data = {}
                for placeholder, val in zip(self.data_placeholder, comb):
                    __data[placeholder] = val
                batches.append(__data)

        elif self.data_placeholder:
            chunks = [data[i:i + QUERY_BATCH_SIZE] for i in range(0, len(data), QUERY_BATCH_SIZE)]
            batches.extend({self.data_placeholder: c} for c in chunks)
        else:
            batches.append({})

        return batches

    # !!! NEED TO ADAPT TO self.formatData() !!!
    #
    # def blocking_send(self, data=None):
    #     __data = self.formatData(data)
    #     for i in range(MAX_RETRIES):
    #         try:
    #             if self.method == "POST":
    #                 response = requests.post(self.URL, json=__data, timeout=3 * 60)
    #             else:
    #                 response = requests.get(self.URL, params=__data, timeout=3 * 60)
    #             if response.status_code == 200:
    #                 return response.json()
    #             else:
    #                 raise RemoteException('Service {} returned an HTTP-Error ({}):\n{}'.format(self.service.name, response.status_code, response.text))
    #         except requests.exceptions.HTTPError as err:
    #             # util_log.error("{0} is not yet ready!".format(self.URL))
    #             pass
    #         except requests.exceptions.ConnectionError as ex:
    #             # util_log.error("Connection Refused: Make sure {0} is up.".format(self.name))
    #             pass
    #         except RemoteException as ex:
    #             # remote exceptions will directly be forwarded and we stop here
    #             raise ex
    #         except Exception as ex:
    #             # util_log.error(str(ex))
    #             pass
    #     raise FailAfterRetries('Giving up after {} retries to reach {}() at {}.'.format(MAX_RETRIES, self.name, self.service.name))

    def send(self, data=None):
        util_log.info( f"call to {self.name} - #params: {len(data[0]) if isinstance(self.data_placeholder, list) else len(data)}")

        __data = self.formatData(data)
        session = FuturesSession()
        for i in range(MAX_RETRIES):
            try:
                # print(f"{datetime.datetime.now()} sending {self.service.name} / {self.name}")
                # start requests
                if self.method == "POST":
                    reqs = [session.post(self.URL, json=d) for d in __data]
                else:
                    reqs = [session.get(self.URL, params=d) for d in __data]

                # collect all results
                res = []
                for future in as_completed(reqs):
                    resp = future.result()
                    if resp.status_code == 200:
                        res.append(resp.json())
                    else:
                        raise RemoteException('Service {} returned an HTTP-Error ({}):\n{}'.format(self.service.name, resp.status_code, resp.text))
                util_log.info( f"    finished call to {self.name}")

                # combine the results, if necessary
                if len(res) == 0:
                    return {}
                elif len(res) == 1:
                    return res[0]
                else:
                    if isinstance(res[0], list):
                        return list(itertools.chain(*res))
                    elif isinstance(res[0], dict):
                        combined = {}
                        for r in res:
                            for k, v in r.items():
                                combined[k] = v
                        return combined
                    else:
                        raise Exception('Implementation missing')

            except requests.exceptions.HTTPError as err:
                # util_log.error("{0} is not yet ready!".format(self.URL))
                pass
            except requests.exceptions.ConnectionError as ex:
                # util_log.error("Connection Refused: Make sure {0} is up.".format(self.name))
                pass
            except RemoteException as ex:
                # remote exceptions will directly be forwarded and we stop here
                raise ex
            except Exception as ex:
                # util_log.error(ex)
                raise ex
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
