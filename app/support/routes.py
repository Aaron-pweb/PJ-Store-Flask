from flask import render_template
from flask_login import login_required
from app.support import support_bp
from app.support.models import Ticket

@support_bp.route("/ticket")
@login_required
def view_tickets():
    tickets = Ticket.query.all()
    return render_template('support/ticket_list.html', tickets=tickets)
