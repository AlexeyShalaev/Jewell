import os

website_service = 'jms_site.service'


def restart_website():
    cmd = f'systemctl restart {website_service}'
    os.system(cmd)
