import logging
from datetime import datetime

from flask import *
from flask_login import login_required, logout_user, current_user

from ManagementSystem.ext.crypt import decrypt_id_with_no_digits, encrypt_id_with_no_digits
from ManagementSystem.ext.database.records import add_record, update_record, delete_record, get_records_by_author, \
    RecordType, get_records
from ManagementSystem.ext.database.relationships import update_relationship, delete_relationship, get_relationships, \
    RelationStatus, add_relationship
from ManagementSystem.ext.database.users import update_social_data, MongoDBResult, get_user_by_id
from ManagementSystem.ext.logistics import check_session, auto_render
from ManagementSystem.ext.notifier import notify_user
from ManagementSystem.ext.search_engine import search_documents
from ManagementSystem.ext.text_filter import TextFilter
from ManagementSystem.ext.tools import set_relations, set_records, get_friends

networking = Blueprint('networking', __name__, url_prefix='/networking', template_folder='templates',
                       static_folder='assets')


# NET WORKING


# Уровень:              networking/feed
# База данных:          User, Relations
# HTML:                 social-feed
@networking.route('/feed', methods=['POST', 'GET'])
@login_required
def feed():
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            if request.form['btn_feed'] == 'add_record':
                record_text = request.form.get("record_text")
                # проверка на нецензурную лексику
                bad_words = TextFilter(record_text).find_bad_words()
                if len(bad_words) > 0:
                    flash(f'В вашем тексте были найдены недопустимые слова: {" ".join(bad_words)}')
                else:
                    add_record(current_user.id, record_text, datetime.now())
                    flash('Вы добавили запись.', 'success')
                    for friend in get_friends(str(current_user.id)):
                        notify_user(get_user_by_id(friend).data, 'Новая запись',
                                    url_for('networking.profile', user_id=current_user.id),
                                    'mdi mdi-new-box',
                                    'info', f'{current_user.first_name} выложил новую запись.')
            elif request.form['btn_feed'] == 'edit_record':
                record_text = request.form.get("record_text")
                record_id = request.form.get("record_id")
                rec_status, rec_id = decrypt_id_with_no_digits(record_id)
                if not rec_status:
                    flash('Не удалось обработать данные.', 'error')
                else:
                    # проверка на нецензурную лексику
                    bad_words = TextFilter(record_text).find_bad_words()
                    if len(bad_words) > 0:
                        flash(f'В вашем тексте были найдены недопустимые слова: {" ".join(bad_words)}')
                    else:
                        update_record(rec_id, 'text', record_text)
                        flash('Вы обновили запись.', 'success')
            elif request.form['btn_feed'] == 'delete_record':
                record_id = request.form.get("record_id")
                rec_status, rec_id = decrypt_id_with_no_digits(record_id)
                if not rec_status:
                    flash('Не удалось обработать данные.', 'error')
                else:
                    delete_record(rec_id)
                    flash('Вы удалили запись.', 'success')
            elif request.form['btn_feed'] == 'profile':
                sex = request.form.get("editSex")
                location = request.form.get("editLocation")
                profession = request.form.get("editProfession")
                university = request.form.get("editUniversity")
                languages = request.form.getlist('editLanguages')
                tags = request.form.get("editTags").split()
                # проверка на нецензурную лексику
                bad_words = TextFilter(f'{location} {profession} {university} {tags}').find_bad_words()
                if len(bad_words) > 0:
                    flash(f'В ваших данных были найдены недопустимые слова: {" ".join(bad_words)}')
                else:
                    update_social_data(current_user.id, sex, location, profession, university, languages, tags)
                    flash('Вы успешно обновили данные', 'success')
                return redirect(url_for('networking.feed'))
            elif request.form['btn_feed'] == 'accept_friend':
                req_id = request.form.get("friend_request_id")
                s, v = decrypt_id_with_no_digits(str(req_id))
                if not s:
                    flash('Не удалось обработать данные.', category='error')
                else:
                    update_relationship(v, 'status', RelationStatus.ACCEPTED.value)
                    flash('Вы успешно приняли заявку.', 'success')
                    notify_user(get_user_by_id(request.form.get("sender_id")).data, 'Новая связь',
                                url_for('networking.profile', user_id=current_user.id),
                                'mdi mdi-human-greeting-proximity',
                                'success', f'{current_user.first_name} теперь в связи с вами.')
            elif request.form['btn_feed'] == 'reject_friend':
                req_id = request.form.get("friend_request_id")
                s, v = decrypt_id_with_no_digits(str(req_id))
                if not s:
                    flash('Не удалось обработать данные.', category='error')
                else:
                    delete_relationship(v)
                    flash('Вы успешно отклонили заявку.', 'success')
            elif request.form['btn_feed'] == 'delete_friend':
                req_id = request.form.get("friend_request_id")
                s, v = decrypt_id_with_no_digits(str(req_id))
                if not s:
                    flash('Не удалось обработать данные.', category='error')
                else:
                    delete_relationship(v)
                    flash('Вы успешно удалили связь.', 'success')
            elif request.form['btn_feed'] == 'revoke_friend':
                req_id = request.form.get("friend_request_id")
                s, v = decrypt_id_with_no_digits(str(req_id))
                if not s:
                    flash('Не удалось обработать данные.', category='error')
                else:
                    delete_relationship(v)
                    flash('Вы успешно отозвали запрос.', 'success')
            elif request.form['btn_feed'] == 'search_records':
                user_records = []
                recs = sorted(get_records_by_author(current_user.id).data, key=lambda rec: rec.time, reverse=True)
                for rec in recs:
                    record_status, record_id = encrypt_id_with_no_digits(str(rec.id))
                    if record_status:
                        user_records.append({
                            'record_id': f'{record_id}',
                            'text': rec.text,
                            'time': rec.time.strftime("%d.%m.%Y %H:%M:%S")
                        })
                fr, frt, frf = set_relations(current_user)
                resp = get_records()
                query = request.form.get("input_query")
                if len(query) == 0:
                    records = set_records(resp)
                else:
                    recs = resp.data
                    docs = [rec.to_document() for rec in recs]
                    result = search_documents(documents=docs, query=query, max_result_document_count=-1)
                    found_records = list(filter(lambda record: str(record.id) in result, recs))
                    found_records.sort(key=lambda rec: result.index(str(rec.id)))
                    records = set_records(resp=MongoDBResult(True, found_records), sort=False)

                render_status, render_html = auto_render()
                if render_status:
                    return render_template(f"{render_html}/networking/social-feed.html", user_records=user_records,
                                           records=records,
                                           friends_requests_to=frt,
                                           friends_requests_from=frf, friends=fr, query=query)
                else:
                    return render_template(render_html)
        except Exception as ex:
            logging.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    user_records = []
    recs = sorted(get_records_by_author(current_user.id).data, key=lambda rec: rec.time, reverse=True)
    for rec in recs:
        if rec.type == RecordType.POST:
            record_status, record_id = encrypt_id_with_no_digits(str(rec.id))
            if record_status:
                user_records.append({
                    'record_id': f'{record_id}',
                    'text': rec.text,
                    'time': rec.time.strftime("%d.%m.%Y %H:%M:%S")
                })
    fr, frt, frf = set_relations(current_user)

    render_status, render_html = auto_render()
    if render_status:
        return render_template(f"{render_html}/networking/social-feed.html", user_records=user_records,
                               records=set_records(resp=get_records()), friends_requests_to=frt,
                               friends_requests_from=frf, friends=fr)
    else:
        return render_template(render_html)


# Уровень:              networking/profile
# База данных:          User
# HTML:                 profile
@networking.route('/profile/<user_id>', methods=['POST', 'GET'])
@login_required
def profile(user_id):
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if str(current_user.id) == str(user_id):
        return redirect(url_for('networking.feed'))

    resp = get_user_by_id(user_id)
    if not resp.success:
        flash('Не удалось найти пользователя.', category='error')
        return redirect(url_for('networking.feed'))
    user = resp.data

    records = []
    resp = get_records_by_author(user_id)
    if resp.success:
        recs = sorted(resp.data, key=lambda rec: rec.time, reverse=True)
        for rec in recs:
            records.append({
                'author': f'{user.first_name} {user.last_name}',
                'text': rec.text,
                'time': rec.time.strftime("%d.%m.%Y %H:%M:%S")
            })

    btn_action = 'add'
    btn_color = 'success'
    btn_icon = 'check'
    btn_text = 'Добавить в друзья'
    relation_id = None
    resp = get_relationships()
    if resp.success:
        rels = resp.data
        for rel in rels:
            if str(rel.sender) == str(current_user.id) and str(rel.receiver) == str(user_id):
                relation_id = rel.id
                if rel.status == RelationStatus.SUBMITTED:
                    btn_action = 'delete'
                    btn_color = 'warning'
                    btn_icon = 'window-close'
                    btn_text = 'Отменить запрос'
                    break
                elif rel.status == RelationStatus.ACCEPTED:
                    btn_action = 'delete'
                    btn_color = 'danger'
                    btn_icon = 'window-close'
                    btn_text = 'Удалить из друзей'
                    break
                else:
                    btn_action = ''
                    btn_color = 'dark'
                    btn_icon = 'progress-question'
                    btn_text = 'Ошибка'
                    break
            elif str(rel.receiver) == str(current_user.id) and str(rel.sender) == str(user_id):
                relation_id = rel.id
                if rel.status == RelationStatus.SUBMITTED:
                    btn_action = 'back'
                    btn_color = 'info'
                    btn_icon = 'backburger'
                    btn_text = 'Перейти к себе'
                    break
                elif rel.status == RelationStatus.ACCEPTED:
                    btn_action = 'delete'
                    btn_color = 'danger'
                    btn_icon = 'window-close'
                    btn_text = 'Удалить из друзей'
                    break
                else:
                    btn_action = ''
                    btn_color = 'dark'
                    btn_icon = 'progress-question'
                    btn_text = 'Ошибка'
                    break

    if request.method == "POST":
        try:
            if btn_action == 'add':
                add_relationship(current_user.id, user_id)
                notify_user(get_user_by_id(user_id).data, 'Запрос в друзья',
                            url_for('networking.profile', user_id=current_user.id),
                            'mdi mdi-human-greeting-variant',
                            'info', f'{current_user.first_name} хочет быть с вами с связи.')
                return redirect(url_for('networking.profile', user_id=user_id))
            elif btn_action == 'delete':
                delete_relationship(relation_id)
                return redirect(url_for('networking.profile', user_id=user_id))
            else:
                return redirect(url_for('networking.feed'))
        except Exception as ex:
            logging.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    render_status, render_html = auto_render()
    if render_status:
        return render_template(f"{render_html}/networking/profile.html", records=records, user=user,
                               btn_action=btn_action, btn_color=btn_color,
                               btn_icon=btn_icon, btn_text=btn_text)
    else:
        return render_template(render_html)


# Уровень:              /relations
# База данных:          User, Relations
# HTML:                 social-relations
@networking.route('/relations', methods=['POST', 'GET'])
@login_required
def networking_relations():
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            pass
        except Exception as ex:
            logging.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    render_status, render_html = auto_render()
    if render_status:
        return render_template(f"{render_html}/networking/social-relations.html")
    else:
        return render_template(render_html)
