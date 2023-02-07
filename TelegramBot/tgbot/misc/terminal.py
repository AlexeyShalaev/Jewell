import os

website_service = 'jms.service'


def restart_website():
    cmd = f'systemctl restart {website_service}'
    os.system(cmd)
