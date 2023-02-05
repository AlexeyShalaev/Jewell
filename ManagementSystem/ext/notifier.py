import logging
from datetime import datetime

from ManagementSystem.ext.database.users import update_notifications, get_users
from ManagementSystem.ext.models.notification import Notification

logger = logging.getLogger(__name__)  # logging


def notify_user(user, region, link, icon, color, text, date=datetime.now()):
    notifications = user.notifications
    notification = Notification.create_notification(region,
                                                    link,
                                                    icon,
                                                    color,
                                                    text,
                                                    date)
    notifications.append(notification)
    update_notifications(user.id, notifications)


def notify_users(region, link, icon, color, text, date=datetime.now()):
    for user in get_users().data:
        try:
            notifications = user.notifications
            notification = Notification.create_notification(region,
                                                            link,
                                                            icon,
                                                            color,
                                                            text,
                                                            date)
            notifications.append(notification)
            update_notifications(user.id, notifications)
        except Exception as ex:
            logger.error(ex)
