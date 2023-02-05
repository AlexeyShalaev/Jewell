from datetime import datetime
from logging import getLogger

from flask import *
from flask_login import *

from ManagementSystem.ext.database.offers import get_offers
from ManagementSystem.ext.database.orders import get_orders_by_client, add_order, delete_order
from ManagementSystem.ext.database.products import get_products, check_product_by_id
from ManagementSystem.ext.logistics import check_session, auto_render
from ManagementSystem.ext.notifier import notify_admins

logger = getLogger(__name__)  # logging
other = Blueprint('other', __name__, url_prefix='/other', template_folder='templates', static_folder='assets')


# Уровень:              other/offers
# База данных:          User, offers
# HTML:                 offers
@other.route('/offers', methods=['POST', 'GET'])
@login_required
def offers():
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            pass
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    render_status, render_html = auto_render()
    if render_status:
        r = get_offers()
        if len(r.data) == 0:
            return render_template(f"{render_html}/other/no-offers.html")
        return render_template(f"{render_html}/other/offers.html", offers=r.data)
    else:
        return render_template(render_html)


# Уровень:              other/products
# База данных:          User, products
# HTML:                 products
@other.route('/products', methods=['POST', 'GET'])
@login_required
def products():
    # check session
    if not check_session():
        logout_user()
        return redirect(url_for("view.landing"))

    if request.method == "POST":
        try:
            if request.form['btn_products'] == 'send_product':
                address = request.form.get("address")
                country = request.form.get("country")
                city = request.form.get("city")
                zip_postal = request.form.get("zip_postal")
                product = request.form.get("product")
                comments = request.form.get("comments")
                if product == 'none':
                    flash('Выберите продукт', 'warning')
                else:
                    if check_product_by_id(product):
                        add_order(product, current_user.id, address, country, city, zip_postal, comments)
                        notify_admins('Новый заказ', url_for('admin.admin_products'), 'mdi mdi-basket-plus',
                                      'primary', f'Новый заказ от пользователя ID={current_user.id}')
                        flash('Ваш заказ принят и передан в обработку', 'success')
                    else:
                        flash('Выбранный товар не существует', 'warning')
            elif request.form['btn_products'] == 'cancel_order':
                order_id = request.form.get("order_id")
                delete_order(order_id)
                notify_admins('Заказ отменен', url_for('admin.admin_products'), 'mdi mdi-basket-off',
                              'danger', f'Отменен заказ ID={order_id} от пользователя ID={current_user.id}')
                flash('Ваш заказ отменен', 'success')
        except Exception as ex:
            logger.error(ex)
            flash('Произошла какая-то ошибка', 'error')

    render_status, render_html = auto_render()
    if render_status:
        return render_template(f"{render_html}/other/products.html", orders=get_orders_by_client(current_user.id).data,
                               products=get_products().data)
    else:
        return render_template(render_html)
