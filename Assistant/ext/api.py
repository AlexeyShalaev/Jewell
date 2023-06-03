import requests

from Assistant import jewell_token, links

snapshot_url = f'{links.server}/api/snapshot'


def snapshot_dump(chat_id='') -> bool:
    try:
        r = requests.post(f'{snapshot_url}/dump', json={"token": jewell_token, "chat_id": chat_id})
        if r.ok:
            res = r.json()
            return res['success']
    except:
        pass
    return False


def delete_record(record) -> bool:
    try:
        r = requests.post(f'{links.server}/api/records/delete',
                          json={"token": jewell_token, "record_id": str(record.id), "user_id": str(record.author)})
        if r.ok:
            res = r.json()
            return res['success']
    except:
        pass
    return False
