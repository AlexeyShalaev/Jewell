from ManagementSystem.ext.models.form import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью Form
Документ: forms
"""


# получение всех форм
def get_forms() -> MongoDBResult:
    res = db.forms.find()
    if res:
        forms = []
        for i in list(res):
            forms.append(Form(i))
        return MongoDBResult(True, forms)
    else:
        return MongoDBResult(False, [])


# получение формы по ID
def get_form_by_id(id) -> MongoDBResult:
    form = db.forms.find_one({'_id': ObjectId(id)})
    if form:
        return MongoDBResult(True, Form(form))
    else:
        return MongoDBResult(False, None)


# добавление формы
def add_form(name, description, content):
    return db.forms.insert_one({
        "name": name,
        "description": description,
        "content": content,
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "status": FormStatus.CLOSED.value
    })


# добавление форм
def add_forms(forms):
    db.forms.insert_many(forms)


# обновление данных формы по ID
def update_form(id, key, value):
    db.forms.update_one({'_id': ObjectId(id)}, {"$set": {key: value}})


# удаление формы по ID
def delete_form(id):
    db.forms.delete_one({
        '_id': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.forms.drop()
