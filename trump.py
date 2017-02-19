import os, time
import slackclient as slack
import peewee

client = slack.SlackClient(os.environ['SLACK_TOKEN'])
db = peewee.MySQLDatabase(os.environ['DB_DB'], host=os.environ['DB_HOST'], user=os.environ['DB_USER'], passwd=os.environ['DB_PASS'])

class SlackEvent(peewee.Model):
    event = peewee.TextField()
    class Meta:
        database = db

if not SlackEvent.table_exists():
    SlackEvent.create_table()

client.rtm_connect()
while True:
    events = client.rtm_read()

    for event in events:
        # Skip any obsolete
        if event['type'] in [ "user_typing", "presence_change", "reconnect_url" ]:
            continue

        db_event = SlackEvent(event=event)
        db_event.save()

    time.sleep(1)
