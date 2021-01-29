from collections import Counter
import socket

def get_ip():
    """
    get the primary local IP address
    https://stackoverflow.com/a/28950776/1169798
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_most_frequent(lst):
    """from a list of values extract the most common one"""
    most_common, num_most_common = Counter(lst).most_common(1)[0]
    return most_common
