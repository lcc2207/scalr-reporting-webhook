# reporting demo webhook

This webhook to kick off scripts you write


# Instance setup.
Execute "bootstrap.sh" on the target install

This will install docker and pull down the reporting-webhook repo.

# Update the uwsgi.ini file with your settings

```ini
[uwsgi]
chdir = /opt/reporting-webhook
http-socket = 0.0.0.0:5018
wsgi-file = webhook.py
callable = app
workers = 1
master = true
plugin = python
env = SCALR_SIGNING_KEY=xxxx
env = ELASTICSEARCH_URL=http://elasticsearch:9200
```

# Launch
execute 'relaunch.sh'
