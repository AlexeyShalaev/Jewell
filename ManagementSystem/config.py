from dataclasses import dataclass
from datetime import datetime
from environs import Env


@dataclass
class DbConfig:
    conn: str  # connection string to database


@dataclass
class FlaskConfig:
    secret_key: str  # app secret key
    """
    import secrets
    print(secrets.token_hex(16))
    """
    app_name: str  # flask app name
    login_manager: dict  # login manager settings


@dataclass
class TgBot:
    token: str
    chat: str  # чат не с ботом, а общий чат с участниками


@dataclass
class Yahad:
    trip: datetime


@dataclass
class Config:  # class config
    db: DbConfig
    flask: FlaskConfig
    tg_bot: TgBot
    yahad: Yahad


def load_config(path: str = ".env"):
    env = Env()
    env.read_env(path)

    return Config(
        db=DbConfig(
            conn=env.str('DB_CONN'),
        ),
        flask=FlaskConfig(
            secret_key=env.str('SECRET_KEY'),
            app_name=env.str('APP_NAME'),
            login_manager={
                'login_view': env.str('LOGIN_VIEW'),
                'login_message': env.str('LOGIN_MESSAGE'),
                'login_message_category': env.str('LOGIN_MESSAGE_CATEGORY'),
            },
        ),
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            chat=env.str("TELEGRAM_CHAT"),
        ),
        yahad=Yahad(trip=datetime.strptime(env.str("YAHAD_TRIP"), "%d.%m.%Y"))
    )
