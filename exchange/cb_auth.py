import requests
import hmac, hashlib, time, base64
from requests.auth import AuthBase
from pathlib import Path
import os
import time

URL = "https://api.pro.coinbase.com/" 

class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        #self.time_phase = 114#time_phase

    def __call__(self, request):

        response = requests.get(URL + 'time')
        epoch = float(response.json()['epoch'])
        our_epoch = time.time()
        time_phase = epoch-our_epoch

        timestamp = str(time.time()+time_phase).encode('utf-8') # TODO Fix time
        print(request.body)
        message = timestamp + request.method.encode('utf-8') + request.path_url.encode('utf-8') + (request.body or ''.encode('utf-8'))
        message = message
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        #signature_b64 = signature.digest().encode('base64').rstrip('\n')
        signature_b64 = base64.b64encode(signature.digest())#.rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


    def update_headers(self, headers, payload, method, url):

        response = requests.get(URL + 'time')
        epoch = float(response.json()['epoch'])
        our_epoch = time.time()
        time_phase = epoch-our_epoch

        print(payload)
        print(method)
        print(url)
        
        #timestamp = str(int(time.time()+time_phase))
        timestamp = str(int(time.time()))
        message = timestamp + method + url.split('?')[0] + str(payload or '')
        signature = hmac.new(self.secret_key.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
        
        headers["accept"] = 'application/json'        
        headers['CB-ACCESS-SIGN'] = signature.hex()
        headers['CB-ACCESS-TIMESTAMP'] = timestamp
        headers['CB-ACCESS-KEY'] = self.api_key
        #headers['CB-ACCESS-PASSPHRASE'] = self.passphrase
        headers['Content-Type'] = 'application/json'
        return headers

    
def get_auth():
    try:
        home = str(Path.home())
    except AttributeError: # For python< 3.5
        home = os.path.expanduser('~')

    sas = 'as.txt'
    sapp = 'app.txt'
    sak = 'ak.txt'
    with open('{}/cb/{}'.format(home, sas), 'r') as f:
        s = f.readline().strip('\n')
        API_SECRET=s
    with open('{}/cb/{}'.format(home, sapp), 'r') as f:
        s = f.readline().strip('\n')
        API_PASS=s
    with open('{}/cb/{}'.format(home, sak), 'r') as f:
        s = f.readline().strip('\n')
        API_KEY=s

    return CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)
    
