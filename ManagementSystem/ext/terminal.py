import os

bot_service = 'jms_bot.service'


def get_telegram_bot_status():
    cmd = f'/usr/bin/systemctl status {bot_service}'
    status = os.system(cmd)
    return status == 0


def stop_telegram_bot():
    cmd = f'/usr/bin/systemctl stop {bot_service}'
    os.system(cmd)


def start_telegram_bot():
    cmd = f'/usr/bin/systemctl start {bot_service}'
    os.system(cmd)


def restart_telegram_bot():
    cmd = f'/usr/bin/systemctl restart {bot_service}'
    os.system(cmd)
