from logging import getLogger

from flask import *

from ManagementSystem.ext.database.forms import get_form_by_id
from ManagementSystem.ext.models.form import FormStatus

logger = getLogger(__name__)  # logging
forms = Blueprint('forms', __name__, url_prefix='/forms', template_folder='templates', static_folder='assets')


# Уровень:              /form_id
# База данных:          User, Forms, FormsAnswers
# HTML:                 form
@forms.route('/<form_id>', methods=['POST', 'GET'])
def submitting_form(form_id):
    if request.method == "POST":
        try:
            # TODO ajax + js
            pass
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

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
        logger.error(ex)
        return render_template("error-500.html")
