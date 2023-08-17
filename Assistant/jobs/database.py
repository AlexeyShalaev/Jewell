from datetime import datetime, timedelta

from Assistant.MongoDB.records import get_records
from Assistant.ext.api import delete_record
from Assistant.MongoDB.visits import truncate as visits_truncate


def delete_records():
    records = get_records().data
    now = datetime.now()
    for record in records:
        if record.lifetime > 0:
            delete_time = record.time + timedelta(days=record.lifetime)
            if now >= delete_time:
                delete_record(record)


def truncating():
    if datetime.now().day == 1:
        # every month clear db
        visits_truncate()
