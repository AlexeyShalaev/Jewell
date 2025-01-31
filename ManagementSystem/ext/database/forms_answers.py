from ManagementSystem.ext.models.form import *
from . import db, MongoDBResult

"""
Это собственно-написанная ORM - для NoSql базы данных MongoDB, для взаимодействия с моделью FormAnswer
Документ: forms_answers
"""


# получение всех ответов
def get_forms_answers() -> MongoDBResult:
    res = db.forms_answers.find()
    if res:
        forms_answers = []
        for i in list(res):
            forms_answers.append(FormAnswer(i))
        return MongoDBResult(True, forms_answers)
    else:
        return MongoDBResult(False, [])


# получение по ID
def get_form_answer_by_id(id) -> MongoDBResult:
    form = db.forms_answers.find_one({'_id': ObjectId(id)})
    if form:
        return MongoDBResult(True, FormAnswer(form))
    else:
        return MongoDBResult(False, None)


# получение по form ID
def get_form_answers_by_id(form_id) -> MongoDBResult:
    res = db.forms_answers.find({'form': ObjectId(form_id)})
    if res:
        forms_answers = []
        for i in list(res):
            forms_answers.append(FormAnswer(i))
        return MongoDBResult(True, forms_answers)
    else:
        return MongoDBResult(False, [])


"""
# получение по form ID
def get_forms_answers_by_author_id(author_id) -> MongoDBResult:
    res = db.forms_answers.find({'author': ObjectId(author_id)})
    if res:
        forms_answers = []
        for i in list(res):
            forms_answers.append(FormAnswer(i))
        return MongoDBResult(True, forms_answers)
    else:
        return MongoDBResult(False, [])
"""


# добавление формы
def add_form_answer(form, answers):
    db.forms_answers.insert_one({
        "form": ObjectId(form),
        # "author": ObjectId(author),
        # "status": FormAnswerStatus.ACTIVE,
        "answers": answers,
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    })


# добавление ответов к форме
def add_forms_answers(forms):
    db.forms_answers.insert_many(forms)


# удаление
def delete_form_answer(id):
    db.forms_answers.delete_one({
        '_id': ObjectId(id)
    })


# удаление
def delete_form_answers(id):
    db.forms_answers.delete_many({
        'form': ObjectId(id)
    })


# очистка Документа
def truncate():
    db.forms_answers.drop()
