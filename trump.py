import os, time
import slackclient as slack
import peewee

# Setup slack client and db
client = slack.SlackClient(os.environ['SLACK_TOKEN'])
db = peewee.MySQLDatabase(os.environ['DB_DB'], host=os.environ['DB_HOST'], user=os.environ['DB_USER'], passwd=os.environ['DB_PASS'])


# Simple event model (we store events as plain json blobs)
class SlackEvent(peewee.Model):
    event = peewee.TextField()

    class Meta:
        database = db


# Create slack event table if needed
if not SlackEvent.table_exists():
    SlackEvent.create_table()


# Connect as real time socket
client.rtm_connect()
while True:
    events = client.rtm_read()

    for event in events:
        # Skip any obsolete events
        if event['type'] in [ "user_typing", "presence_change", "reconnect_url" ]:
            continue

        # Save all other events
        db_event = SlackEvent(event=event)
        db_event.save()

    # Prevent trashing
    time.sleep(1)
