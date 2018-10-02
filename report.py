#!/usr/bin/env python
from __future__ import print_function

import json
import logging
import sys
import requests
import dateutil.parser

def format_item(doc):
    fields = [doc['timestamp'], doc['eventName']]
    for gv in ['SCALR_EVENT_SERVER_ID', 
               'SCALR_EVENT_EXTERNAL_IP',
               'SCALR_EVENT_INTERNAL_IP', 
               'SCALR_EVENT_SERVER_HOSTNAME',
               'SCALR_EVENT_SERVER_TYPE',
               'SCALR_EVENT_CLOUD_LOCATION',
               ]:
        fields.append(doc['data'].get(gv, ''))
    return ','.join(fields)

logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) != 4:
    print('Usage: report.py start_date end_date output_file')
    sys.exit(1)

start = dateutil.parser.parse(sys.argv[1])
end = dateutil.parser.parse(sys.argv[2])
output = sys.argv[3]

query = json.dumps( { "query" : 
                        { "range" : { 
                            "timestamp" : { 
                                "gte" : start.isoformat(), 
                                "lt" : end.isoformat()
                                }
                            }
                        }
                    })

print(query)

res = requests.get('http://localhost:9200/_all/scalr-event/_search', data=query)
data = json.loads(res.text)

docs = data['hits']['hits']
print(len(docs))

with open(output, 'w') as f:
    for d in docs:
        f.write(format_item(d['_source']) + '\n')
