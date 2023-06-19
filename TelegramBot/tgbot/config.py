from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    conn: str  # connection string to database


@dataclass
class TgBot:
    token: str


@dataclass
class API:
    jewell: str


@dataclass
class Links:
    server: str
    jewell: str
    chat: str
    courses: str
    courses_image: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    api: API
    links: Links


def load_config(path: str = '.env'):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN")
        ),
        db=DbConfig(
            conn=env.str('DB_CONN')
        ),
        api=API(
            jewell=env.str('JEWELL_TOKEN')
        ),
        links=Links(
            server=env.str('URL_SERVER'),
            jewell=env.str('URL_JEWELL'),
            chat=env.str('URL_CHAT'),
            courses=env.str('URL_COURSES'),
            courses_image=env.str('URL_COURSES_IMAGES')
        )
    )
