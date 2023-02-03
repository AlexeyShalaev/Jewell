import os


def get_telegram_bot_status():
    cmd = 'systemctl status jnet.service'
    status = os.system(cmd)
    print('-------------------------')
    print(status)
