from bike_sharing_app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class User(db.Model ,UserMixin):
    """Create a table Users on the candidature database
    Args:
        db.Model: Generates columns for the table
        UserMixin: Generates an easy way to provide a current_user
    """
    id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
    email_address = db.Column(db.String(length=50),nullable=False, unique=True)
    password_hash = db.Column(db.String(length=200), nullable=False)
    
    def __repr__(self):
        return f'{self.last_name} {self.first_name}'
    
    @classmethod
    def find_by_mail(cls, mail):
        return cls.query.filter_by(email_adress=mail).first()
    
def init_db():
    db.drop_all()
    db.create_all()
    User(email_address = "cb@gmail.com", password_hash = generate_password_hash("admin", method="sha256"))
    User(email_address = "fm@gmail.com", password_hash = generate_password_hash("asmin", method="sha256"))
    User(email_address = "rb@gmail.com", password_hash = generate_password_hash("admin", method="sha256"))
    User(email_address = "mc@gmail.com", password_hash = generate_password_hash("admin", method="sha256"))
    
    