from datetime import datetime
import logging

from Assistant.MongoDB.users import update_notifications, get_users_by_role
from Assistant.models.notification import Notification
from Assistant.models.userModel import Role


def notify_user(user, region, link, icon, color, text, date=datetime.now()):
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
        logging.error(ex)


def notify_admins(region, link, icon, color, text, date=datetime.now()):
    for admin in get_users_by_role(Role.ADMIN).data:
        try:
            notifications = admin.notifications
            notification = Notification.create_notification(region,
                                                            link,
                                                            icon,
                                                            color,
                                                            text,
                                                            date)
            notifications.append(notification)
            update_notifications(admin.id, notifications)
        except Exception as ex:
            logging.error(ex)
