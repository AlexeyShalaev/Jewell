import json
import logging

from flask import *

from ManagementSystem.ext.database.forms import get_form_by_id
from ManagementSystem.ext.database.forms_answers import add_form_answer
from ManagementSystem.ext.models.form import FormStatus

forms = Blueprint('forms', __name__, url_prefix='/forms', template_folder='templates', static_folder='assets')


# Уровень:              /form_id
# База данных:          User, Forms, FormsAnswers
# HTML:                 form
@forms.route('/<form_id>', methods=['POST', 'GET'])
def submitting_form(form_id):
    if request.method == "POST":
        try:
            answers = json.loads(request.form['answers'])
            add_form_answer(form_id, answers)
            flash('Форма успешно отправлена!', 'success')
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        except Exception as ex:
            logging.error(ex)
            flash('Не удалось отправить форму!', 'error')
            return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}

    try:
        resp = get_form_by_id(form_id)
        if not resp.success:
            flash('Форма не найдена!', 'error')
            return redirect(url_for('view.landing'))

        form = resp.data

        if form.status != FormStatus.OPENED:
            flash('Форма закрыта.', 'info')
            return redirect(url_for('view.landing'))

        return render_template("form.html", form=form)
    except Exception as ex:
        logging.error(ex)
        return render_template("error-500.html")
