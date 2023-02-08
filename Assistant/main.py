import os
import sys
import schedule
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from Assistant.jobs.database import delete_records
from Assistant.jobs.snapshot import dump
from Assistant.jobs.website import check_website

schedule.every().week.do(dump)
schedule.every().day.do(check_website)
schedule.every().day.do(delete_records)

while True:
    schedule.run_pending()
    time.sleep(1)
