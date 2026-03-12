from app.extensions import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('cart', uselist=False))
    # Relationship to items
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade="all, delete-orphan")

    def get_total(self):
        total = 0
        for item in self.items:
            price = item.product.price
            if item.variant and item.variant.price_override:
                price = item.variant.price_override
            total += price * item.quantity
        return total

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=True)

    product = db.relationship('Product')
    variant = db.relationship('ProductVariant')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Paid, Shipped, Cancelled
    total_amount = db.Column(db.Float, nullable=False)
    tx_ref = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=True) # Check if nullable needed, likely Yes for now or No if strict
    
    user = db.relationship('User', backref='orders')
    address = db.relationship('Address')
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    variant_name = db.Column(db.String(100), nullable=True) # Snapshot of variant details
    variant_id = db.Column(db.Integer, nullable=True) # Link to variant (if it still exists)

    product = db.relationship('Product')
