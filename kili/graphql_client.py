import websocket
import threading
import random
import string
import json
import time

from six.moves import urllib


class GraphQLClient:
    def __init__(self, endpoint, session=None):
        self.endpoint = endpoint
        self.session = session
        self.token = None
        self.headername = None

    def execute(self, query, variables=None):
        return self._send(query, variables)

    def inject_token(self, token, headername='Authorization'):
        self.token = token
        self.headername = headername

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers[self.headername] = '{}'.format(self.token)

        if self.session is not None:
            try:
                number_of_trials = 3
                for n in range(number_of_trials):
                    req = self.session.post(self.endpoint, json.dumps(
                        data).encode('utf-8'), headers=headers)
                    if req.status_code == 200:
                        break
                    time.sleep(1)
                return req.json()
            except Exception as e:
                print('Request failed with error:\n')
                if req:
                    print(req.content)
                print('')
                raise e

        req = urllib.request.Request(
            self.endpoint, json.dumps(data).encode('utf-8'), headers)
        try:
            response = urllib.request.urlopen(req)
            str_json = response.read().decode('utf-8')
            print('>>>>', str_json)
            return json.loads(str_json)
        except urllib.error.HTTPError as e:
            print((e.read()))
            print('')
            raise e


GQL_WS_SUBPROTOCOL = "graphql-ws"


class SubscriptionGraphQLClient:
    """
    A simple GraphQL client that works over Websocket as the transport
    protocol, instead of HTTP.
    This follows the Apollo protocol.
    https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
    """

    def __init__(self, url):
        self.ws_url = url
        self._conn = websocket.create_connection(self.ws_url,
                                                 on_message=self._on_message,
                                                 subprotocols=[GQL_WS_SUBPROTOCOL])
        self._conn.on_message = self._on_message
        self._subscription_running = False
        self._st_id = None

    def _on_message(self, message):
        data = json.loads(message)
        # skip keepalive messages
        if data['type'] != 'ka':
            print(message)

    def _conn_init(self, headers=None):
        payload = {
            'type': 'connection_init',
            'payload': {'headers': headers}
        }
        self._conn.send(json.dumps(payload))
        self._conn.recv()

    def _start(self, payload):
        _id = gen_id()
        frame = {'id': _id, 'type': 'start', 'payload': payload}
        self._conn.send(json.dumps(frame))
        return _id

    def _stop(self, _id):
        payload = {'id': _id, 'type': 'stop'}
        self._conn.send(json.dumps(payload))
        return self._conn.recv()

    def query(self, query, variables=None, headers=None):
        self._conn_init(headers)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        _id = self._start(payload)
        res = self._conn.recv()
        self._stop(_id)
        return res

    def subscribe(self, query, variables=None, headers=None, callback=None):
        self._conn_init(headers)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        _cc = self._on_message if not callback else callback
        _id = self._start(payload)

        def subs(_cc):
            self._subscription_running = True
            while self._subscription_running:
                r = json.loads(self._conn.recv())
                if r['type'] == 'error' or r['type'] == 'complete':
                    print(r)
                    self.stop_subscribe(_id)
                    break
                elif r['type'] != 'ka':
                    _cc(_id, r)
                time.sleep(1)

        self._st_id = threading.Thread(target=subs, args=(_cc,))
        self._st_id.start()
        return _id

    def stop_subscribe(self, _id):
        self._subscription_running = False
        self._st_id.join()
        self._stop(_id)

    def close(self):
        self._conn.close()


# generate random alphanumeric id
def gen_id(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
