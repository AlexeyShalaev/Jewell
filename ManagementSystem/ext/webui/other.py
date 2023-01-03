import logging

from flask import *
from flask_login import *

from ManagementSystem.ext.database.offers import get_offers
from ManagementSystem.ext.logistics import check_session, auto_render

logger = logging.getLogger(__name__)  # logging
other = Blueprint('other', __name__, url_prefix='/other', template_folder='templates', static_folder='assets')


# Уровень:              other/feed
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


# Уровень:              other/feed
# База данных:          User, orders
# HTML:                 orders
@other.route('/orders', methods=['POST', 'GET'])
@login_required
def orders():
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
        return render_template(f"{render_html}/other/orders.html")
    else:
        return render_template(render_html)
