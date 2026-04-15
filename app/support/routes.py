from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.support import support_bp
from app.support.models import Ticket, MessageThread, Message
from app.products.models import Product

@support_bp.route("/ticket")
@login_required
def view_tickets():
    tickets = Ticket.query.all()
    return render_template('support/ticket_list.html', tickets=tickets)

@support_bp.route("/messages")
@login_required
def messages():
    if current_user.role == 'seller':
        threads = MessageThread.query.filter_by(seller_id=current_user.id).all()
    else:
        threads = MessageThread.query.filter_by(customer_id=current_user.id).all()
    return render_template('support/messages.html', threads=threads)

@support_bp.route("/messages/start/<int:product_id>", methods=['POST'])
@login_required
def start_thread(product_id):
    product = Product.query.get_or_404(product_id)

    # Check if a thread already exists
    thread = MessageThread.query.filter_by(
        customer_id=current_user.id,
        seller_id=product.seller_id,
        product_id=product.id
    ).first()

    if not thread:
        thread = MessageThread(
            customer_id=current_user.id,
            seller_id=product.seller_id,
            product_id=product.id
        )
        db.session.add(thread)
        db.session.commit()

    return redirect(url_for('support.view_thread', thread_id=thread.id))

@support_bp.route("/messages/thread/<int:thread_id>", methods=['GET', 'POST'])
@login_required
def view_thread(thread_id):
    thread = MessageThread.query.get_or_404(thread_id)

    # Authorization
    if current_user.id not in [thread.customer_id, thread.seller_id]:
        abort(403)

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            message = Message(
                thread_id=thread.id,
                sender_id=current_user.id,
                content=content
            )
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('support.view_thread', thread_id=thread.id))

    # Mark messages as read
    unread_messages = Message.query.filter_by(thread_id=thread.id, is_read=False).filter(Message.sender_id != current_user.id).all()
    for msg in unread_messages:
        msg.is_read = True
    if unread_messages:
        db.session.commit()

    return render_template('support/thread.html', thread=thread)
