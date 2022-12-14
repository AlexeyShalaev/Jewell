from flask_login import UserMixin
from ..models.jewell import User
import logging

logger = logging.getLogger(__name__)  # logging


class UserLogin(UserMixin):
    user: User

    def fromDB(self, phone_number):
        try:
            self.user = User.find_one(User.phone_number == phone_number).run()
            # TODO проверка, что пользователь найден
        except Exception as ex:
            logger.error(str(ex))
        return self
