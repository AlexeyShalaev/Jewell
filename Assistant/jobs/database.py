from datetime import datetime, timedelta

from Assistant.MongoDB.records import get_records
from Assistant.ext.api import delete_record


def delete_records():
    records = get_records().data
    now = datetime.now()
    for record in records:
        if record.lifetime > 0:
            delete_time = record.time + timedelta(days=record.lifetime)
            if now >= delete_time:
                delete_record(record)
