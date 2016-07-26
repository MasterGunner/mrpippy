import gevent.monkey

gevent.monkey.patch_all()

import json
import logging
import requests

from gpippy import Client


def main(host, url, level='INFO', interval='5'):
    interval = float(interval)
    logging.basicConfig(level=level)
    client = Client(host, on_update=on_update)
    while not client.finished.ready():
        gevent.sleep(interval)
        if client.pipdata.root:
            r = requests.patch(url, data=json.dumps(client.pipdata.root.value, indent=4))
    client.wait()


def on_update(value):
    logging.info("Updated value: {}".format(value))


if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
