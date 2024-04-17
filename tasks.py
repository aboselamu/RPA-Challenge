# import html
import time
import requests
import logging
from pathlib import Path
from datetime import datetime, timedelta
from datetime import datetime
from robocorp.tasks import task
from RPA.Robocorp.WorkItems import WorkItems
from robocorp import vault
from robocorp.tasks import get_output_dir
from RPA.Excel.Files import Files as Excel

from RPA.Browser.Selenium import Selenium 
logger = logging.getLogger(__name__)
# import re

@task
def process_news():
    work_items = WorkItems()
    if not work_items.inputs:
        print("No input work items available.")
        pass

    for item in work_items.inputs:
        with item:
            search_phrase = item.payload.get("search_phrase")
            number_of_months = item.payload.get("number_of_months")
            print(f"Processing news for: {search_phrase} over the past {number_of_months} months.")
            # Your processing logic here