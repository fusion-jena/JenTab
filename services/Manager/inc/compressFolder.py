import zlib


def compressFolder(path):
    """
    send a zip file including the contents of the given folder
    https://stackoverflow.com/a/44387566/1169798
    """
    compressor = zlib.compressobj()
    for x in range(10000):
        chunk = compressor.compress(f"this is my line: {x}\n".encode())
        if chunk:
            yield chunk
    yield compressor.flush()
