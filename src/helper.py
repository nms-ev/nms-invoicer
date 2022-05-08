from datetime import datetime
import os
from values import Events
from typing import Dict
import requests
import json
from api import get_events
from os.path import isfile
from os.path import isdir

class InputError(Exception):
    pass

def strip(v: dict, user_id: str) -> Dict[str,float]:
    
    event_name = v[Events.INVOICE_SELECT_EVENT.value][Events.INVOICE_SELECT_EVENT.value]\
        ["selected_option"]["text"]["text"]
        
    invoice_date = v[Events.INVOICE_SELECT_DATE.value][Events.INVOICE_SELECT_DATE.value]["selected_date"]
    user = user_id
    cost = v[Events.INVOICE_SELECT_AMOUNT.value]["plain_text_input-action"]["value"]
    purpose = v[Events.INVOICE_SELECT_DESCRIPTION.value]["purpose"]["value"]
    
    # Capitalize first letter
    purpose = purpose[0].upper() + purpose[1:]
    
    
    try:
        cost = float(cost)
    except:
        raise InputError("Bitte Ganzzahl oder "
                         "Englisches Format nutzen. Bsp: 2 oder 12.69",
                         "invoice_cost") 
    
    if str(cost)[::-1].find(".") > 2:
        raise InputError("Mehr als zwei Nachkommastellen gibt es "
                         "nicht amk.", "invoice_cost")
    
    out = {
        "invoice_date": invoice_date,
        "event_name"  : event_name,
        "purpose"     : purpose,
        "cost"        : cost,
        "user"        : user
    }
    
    return out


                
class Datafile:
    def __init__(self, event_name) -> None:
        
        datapath = "db/"
        extension = ".data"
        
        self.event_name = event_name
        self.is_new_file = False
        
        self.filename = datapath + event_name + extension
        self.date_of_event = get_events()[event_name]["date"]
        
        if not isdir(datapath):
            os.mkdir(datapath)
        
        if not isfile(self.filename):
            self.is_new_file = True
            with open(self.filename, "w+"):
                pass

    def event_date(self) -> str:
        """Get the event date from the event name
        the user clicked on. 

        Args:
            submitted_name (str): Event name formatted as
            'location_date'

        Returns:
            _type_: date of event as YYYY-MM-DD
        """
        date = self.date_of_event
        date = datetime.strptime(date,"%Y-%m-%d")
        date = datetime.strftime(date, "%d.%m.%Y")
        
        return date

    def store(self, d: dict) -> None:
        """Store a given invoice dict to the event data file.
        If it does not exist yet, build it.

        Args:
            d (dict): Invoice dict containg:
                        - Event Name
                        - Event Date
                        - Invoice Cost
                        - User
            
        """

        # Build a header if the file is new
        if self.is_new_file:
            header = ",".join([k for k in d.keys()])
        
        # Build row
        row = ",".join([str(v) for v in d.values()])
        
        
        with open(self.filename,"a") as file:
            if self.is_new_file:
                file.write(header + "\n")
            file.write(row + "\n")
        
        self.is_new_file = False