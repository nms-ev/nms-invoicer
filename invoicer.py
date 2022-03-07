import json
import os
import dynamics as dyn
from inserter import LatexBuilder
from datetime import datetime
from helper import Datafile, get_eventlist, strip, InputError
from dotenv import load_dotenv
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt import App
from json_blocks import __path__
    
load_dotenv() 
app = App(token=os.environ["TOKEN"],signing_secret=os.environ["SIGNING_SECRET"])

# Add functionality here
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    
    # Parse the home_tab_view json file
    with open(__path__[0] + "/home_tab_view.json", "r") as file:
        home = json.load(file)
    
    try:
    # Push a view to the Home tab
        client.views_publish(
      # the user that opened your app's app home
        user_id=event["user"],
      # the view object that appears in the app home
        view = json.dumps(home))
  
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

# Say something upon mentioning the bot
@app.event("app_mention")
def event_test(say):
    say("What's up?")

@app.message("")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    user = message["user"]
    say(text=f"Hey there <@{user}>!")

# Open the invoice modal via its global shortcut
@app.global_shortcut("open-invoice-modal")
def open_invoice_modal(ack, shortcut, client):
  
  ack()
  
  client.views_open(
        trigger_id=shortcut["trigger_id"],
        # A simple view payload for a modal
        view = dyn.prepare_modal(
            dyn.create_event_list(
                get_eventlist()
                )
            )
    )

# Open the invoice modal but this time by pressing the corresponding button
# in the home tab
@app.action("home-submit-button")
def open_invoice_modal_from_home(ack, body, client):
    
    # Ackowledge the incoming request
    ack()
    
    # Open the modal
    client.views_open(
        trigger_id = body["trigger_id"],
        view = dyn.prepare_modal(
            dyn.create_event_list(
                get_eventlist()
                )
            )
    )

@app.action("static_select-action")
def handle_selection(ack, body, logger):
    ack()
    
@app.action("users_select-action")
def handle_some_action(ack, body, logger):
    ack()
    
@app.action("invoice-date-select")
def handle_datepicker(ack, body, logger):

    invoice_date = body["actions"][0]["selected_date"]
    # Check if selected date lies in the future
    today = datetime.today()
    to_check = datetime.strptime(invoice_date,"%Y-%m-%d")
    if today < to_check:
        #raise InputError("Du kannst keine Rechnungen aus der "
        #                  "Zukunft einreichen.", "event_date")
        errors = {}
        errors["invoice-date-select"] = ("Du kannst keine Rechnungen aus der "
                                         "Zukunft einreichen.")
        ack(response_action="errors",errors=errors)
    else:
        ack()
    return
    
@app.view("invoice")
def handle_view_events(ack, body, logger, client):
    
    values: dict = body["view"]["state"]["values"]
    user: str = body["user"]["id"]
    
    try:
        stripped: dict = strip(values, user)
    except InputError as e:
        errors = {}
        errors[e.args[1]] = e.args[0]
        ack(response_action="errors",errors=errors)
        return
    
    ack()
    file = Datafile(stripped["event_name"])
    file.store(stripped)
    builder = LatexBuilder(file.filename)
    builder.set()
    builder.compile()
    
    return

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SOCKET_TOKEN"]).start()