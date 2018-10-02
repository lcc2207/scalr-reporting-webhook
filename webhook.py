#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import abort

import pytz
import string
import random
import json
import logging
import binascii
import dateutil.parser
import hmac
import os
import requests
import subprocess

from requests.exceptions import ConnectionError
from hashlib import sha1
from datetime import datetime

from elasticsearch import Elasticsearch

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# Configuration variables
SCALR_SIGNING_KEY = os.getenv('SCALR_SIGNING_KEY', '')
ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL', 'elasticsearch')

for var in ['SCALR_SIGNING_KEY', 'ELASTICSEARCH_URL']:
    logging.info('Config: %s = %s', var, globals()[var] if 'PASS' not in var else '*' * len(globals()[var]))

@app.route('/reporting/', methods=['POST'])
def webhook_listener():
    try:
        if not validate_request(request):
            abort(403)

        data = json.loads(request.data)
        if not 'eventName' in data or not 'data' in data:
            abort(404)

        logging.info(data)
        return recordEvent(data)

    except Exception as e:
        logging.exception('Error processing this request')
        abort(500)

def indexName():
    return 'scalr-events-{}'.format(datetime.utcnow().date().isoformat())

def recordEvent(data):
    es = Elasticsearch(ELASTICSEARCH_URL)
    logging.info('-=-=-=-=-=')
    logging.info(ELASTICSEARCH_URL)
    logging.info('-=-=-=-=-=')
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
    timestamp = dateutil.parser.parse(data['timestamp'])
    data['timestamp'] = timestamp.isoformat()
    r = requests.post('{}/{}/scalr-event/'.format(ELASTICSEARCH_URL, index), data=json.dumps(data))
    return r.text

def validate_request(request):
    if 'X-Signature' not in request.headers or 'Date' not in request.headers:
        logging.debug('Missing signature headers')
        return False
    date = request.headers['Date']
    body = request.data
    expected_signature = binascii.hexlify(hmac.new(SCALR_SIGNING_KEY, body + date, sha1).digest())
    if expected_signature != request.headers['X-Signature']:
        logging.debug('Signature does not match')
        return False
    date = dateutil.parser.parse(date)
    now = datetime.now(pytz.utc)
    delta = abs((now - date).total_seconds())
    return delta < 300

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
