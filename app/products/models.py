from app.extensions import db

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    seller = db.relationship('User', backref='products')
    variants = db.relationship('ProductVariant', backref='product', lazy=True)

class ProductVariant(db.Model):
    __tablename__ = "product_variant"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_name = db.Column(db.String(50), nullable=False) # e.g. "Size: Large" or just "Large"
    stock = db.Column(db.Integer, default=0)
    price_override = db.Column(db.Float, nullable=True) # If set, use this price instead of product.price
