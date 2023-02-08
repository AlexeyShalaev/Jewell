import os

website_service = 'jms_site.service'


def get_website_status():
    cmd = f'systemctl status {website_service}'
    status = os.system(cmd)
    return status == 0


def restart_website():
    cmd = f'systemctl restart {website_service}'
    os.system(cmd)
