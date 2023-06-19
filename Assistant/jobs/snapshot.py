from Assistant.ext.api import snapshot_dump
from Assistant.ext.notifier import notify_admins


def dump():
    if snapshot_dump():
        notify_admins('Резервное копирование',
                      f'/admin/configuration/backup',
                      'mdi mdi-backup-restore',
                      'danger',
                      f'Создана автоматическая резервная копия.')
