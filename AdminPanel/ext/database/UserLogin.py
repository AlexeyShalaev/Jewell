from flask_login import UserMixin
from ..models.jewell import User
import logging

logger = logging.getLogger(__name__)  # logging


class UserLogin(UserMixin):
    __user: User  # user model

    def fromDB(self, phone_number: str):
        try:
            self.__user = User.find_one(User.phone_number == phone_number).run()
            if self.__user is None:
                return False
            else:
                return self
        except Exception as ex:
            logger.error(str(ex))
            return False

    def create(self, user: User):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user.id)
