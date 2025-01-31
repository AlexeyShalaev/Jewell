import logging
from datetime import datetime

from ManagementSystem.ext.database.users import update_notifications, get_users, get_users_by_role
from ManagementSystem.ext.models.notification import Notification
from ManagementSystem.ext.models.userModel import Role


def notify_user(user, region, link, icon, color, text, date=None):
    if date is None:
        date = datetime.now()
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


def notify_users(region, link, icon, color, text, date=None):
    if date is None:
        date = datetime.now()
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
            logging.error(ex)


def notify_admins(region, link, icon, color, text, date=None):
    if date is None:
        date = datetime.now()
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
