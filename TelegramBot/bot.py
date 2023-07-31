import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.config import load_config

from tgbot.filters.__init__ import register_filters
from tgbot.handlers.__init__ import register_handlers
from tgbot.middlewares.__init__ import register_middlewares


async def main():
    logging.basicConfig(
        filename='bot.log',
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        datefmt='%H:%M:%S',
        level=logging.INFO,
    )
    logging.info("Starting bot")
    config = load_config()

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_middlewares(dp)
    register_filters(dp)
    register_handlers(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
