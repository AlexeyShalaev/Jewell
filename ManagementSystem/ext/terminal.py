import os

bot_service = 'jnet.service'


def get_telegram_bot_status():
    cmd = f'systemctl status {bot_service}'
    status = os.system(cmd)
    return status == 0


def stop_telegram_bot():
    cmd = f'systemctl stop {bot_service}'
    status = os.system(cmd)
    print('---------------------')
    print(status)
    print('---------------------')


def start_telegram_bot():
    cmd = f'systemctl start {bot_service}'
    status = os.system(cmd)
    print('---------------------')
    print(status)
    print('---------------------')


def restart_telegram_bot():
    cmd = f'systemctl restart {bot_service}'
    status = os.system(cmd)
    print('---------------------')
    print(status)
    print('---------------------')
