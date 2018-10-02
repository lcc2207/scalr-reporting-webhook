from flask import Flask
from flask import request
from flask import abort
import pytz
import json
import logging
import binascii
import dateutil.parser
import hmac
from hashlib import sha1
from datetime import datetime
from elasticsearch import Elasticsearch
import requests

config_file = '/opt/webhook/config.json'

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# will be overridden if present in config_file
ELASTICSEARCH_URLS = ['http://elasticsearch:9200']
SCALR_SIGNING_KEY = 'scalr signing key'

@app.route("/", methods=['POST'])
def webhook_listener():
    try:
        if not validateRequest(request):
            abort(403)

        data = json.loads(request.data)
        if not 'eventName' in data or not 'data' in data:
            abort(404)

        return recordEvent(data)

    except Exception as e:
        logging.exception('Error processing this request')
        abort(500)

def indexName():
    return 'scalr-events-{}'.format(datetime.utcnow().date().isoformat())

def recordEvent(data):
    es = Elasticsearch(ELASTICSEARCH_URLS)
    index = indexName()
    es.indices.create(index=index, ignore=400, body={
            'mappings': {
                'scalr-event': {
                    'properties': {
                        'timestamp': {
                            'type': 'date'
                        }
                    }
                }
            }
        })
    #return json.dumps(es.index(index=indexName(), body=data, doc_type='scalr-event', op_type='create'))
    timestamp = dateutil.parser.parse(data['timestamp'])
    data['timestamp'] = timestamp.isoformat()
    r = requests.post('{}/{}/scalr-event/'.format(ELASTICSEARCH_URLS[0], index), data=json.dumps(data))
    return r.text

def validateRequest(request):
    if not 'X-Signature' in request.headers or not 'Date' in request.headers:
        return False
    date = request.headers['Date']
    body = request.data
    expected_signature = binascii.hexlify(hmac.new(SCALR_SIGNING_KEY, body + date, sha1).digest())
    if expected_signature != request.headers['X-Signature']:
        return False
    date = dateutil.parser.parse(date)
    now = datetime.now(pytz.utc)
    delta = abs((now - date).total_seconds())
    return delta < 300

def loadConfig(filename):
    with open(config_file) as f:
        options = json.loads(f.read())
        for key in options:
            if key in ['ELASTICSEARCH_URLS']:
                logging.info('Loaded config: {}'.format(key))
                globals()[key] = options[key]
            elif key in ['SCALR_SIGNING_KEY']:
                logging.info('Loaded config: {}'.format(key))
                globals()[key] = options[key].encode('ascii')

loadConfig(config_file)

if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0')

