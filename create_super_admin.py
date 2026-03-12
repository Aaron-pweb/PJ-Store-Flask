from app import create_app
from app.extensions import db
from app.auth.models import User
import getpass

app = create_app()

def create_super_admin():
    with app.app_context():
        print("--- Create Super Admin ---")
        username = input("Username: ")
        email = input("Email: ")
        password = getpass.getpass("Password: ")
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(user_name=username).first():
            print("Error: User already exists.")
            return

        user = User(
            full_name="Super Admin",
            user_name=username,
            email=email,
            password=password, # will be hashed by set_password
            role='super_admin',
            is_approved=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        print(f"Super Admin '{username}' created successfully!")

if __name__ == "__main__":
    create_super_admin()
