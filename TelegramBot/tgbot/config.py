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
class Config:
    tg_bot: TgBot
    db: DbConfig
    api: API


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
        )
    )
