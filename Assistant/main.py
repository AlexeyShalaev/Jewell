import os
import sys
import time

import schedule

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from Assistant.jobs.database import delete_records, truncating
from Assistant.jobs.snapshot import dump
from Assistant.jobs.website import check_website
from Assistant.jobs.logs import clear_logs

schedule.every().monday.do(dump)
schedule.every().sunday.do(clear_logs)
schedule.every().day.do(check_website)
schedule.every().day.do(delete_records)
schedule.every().day.at("23:00").do(truncating)  # monthly

while True:
    schedule.run_pending()
    time.sleep(1)
