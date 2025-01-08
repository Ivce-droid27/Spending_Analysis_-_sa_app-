from con_sqlalchemy import db

class User_info(db.Model):
    __tablename__ = "users_info"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    pay_check = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(65), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'p_check': self.pay_check,
            'email': self.email,
            'age': self.age
        }