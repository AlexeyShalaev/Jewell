from . import db

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Visit
Документ: visits
"""


# очистка Документа
def truncate():
    db.visits.drop()
