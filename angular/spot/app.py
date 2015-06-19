from bottle import route, run, template
import requests


class Spotify(object):
    base = 'https://api.spotify.com'
    version = 'v1'

    def build(self, endpoint, params):
        url = '%s/%s/%s/?%s' % (
            self.base, self.version, endpoint,
            '&'.join(['%s=%s' % (i, params[i]) for i in params]))
        return url

    def search(self, key, stype='track'):
        results = requests.get(self.build('search', {'q': key, 'type': stype}))
        return results


@route('/')
def index():
    return template('index')


@route('/search/:key')
def search(key):
    s = Spotify()
    results = s.search(key)
    return results.json()

run(host='0.0.0.0', port=8888, reloader=True)
