from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    conn: str  # connection string to database


@dataclass
class FlaskConfig:
    secret_key: str  # app secret key
    api_token: str  # api secret key
    """
    import secrets
    print(secrets.token_hex(16))
    """
    app_name: str  # flask app name
    login_manager: dict  # login manager settings
    session_max_age: int


@dataclass
class TgBot:
    token: str
    chat: str  # чат не с ботом, а общий чат с участниками


@dataclass
class Config:  # class config
    db: DbConfig
    flask: FlaskConfig
    tg_bot: TgBot


def load_config(path: str = ".env"):
    env = Env()
    env.read_env(path)

    return Config(
        db=DbConfig(
            conn=env.str('DB_CONN'),
        ),
        flask=FlaskConfig(
            secret_key=env.str('SECRET_KEY'),
            api_token=env.str('API_TOKEN'),
            app_name=env.str('APP_NAME'),
            login_manager={
                'login_view': env.str('LOGIN_VIEW'),
                'login_message': env.str('LOGIN_MESSAGE'),
                'login_message_category': env.str('LOGIN_MESSAGE_CATEGORY'),
            },
            session_max_age=env.int('SESSION_MAX_AGE'),
        ),
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            chat=env.str("TELEGRAM_CHAT"),
        )
    )
