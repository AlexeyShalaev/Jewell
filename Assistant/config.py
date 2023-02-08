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
    jewell: str


@dataclass
class Config:  # class config
    db: DbConfig
    tg_bot: TgBot
    api: API
    links: Links


def load_config(path: str = ".env"):
    env = Env()
    env.read_env(path)

    return Config(
        db=DbConfig(
            conn=env.str('DB_CONN'),
        ),
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN")
        ),
        api=API(
            jewell=env.str('JEWELL_TOKEN')
        ),
        links=Links(
            jewell=env.str('URL_JEWELL')
        )
    )
