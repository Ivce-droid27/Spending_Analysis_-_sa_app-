from con_sqlalchemy import db

class User_info(db.Model):
    __tablename__ = "users_info"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(65), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    pay_check = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            'user_id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'pay_check': self.pay_check
        }


class Total(db.Model):
    __tablename__ = "total_spent"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,  db.ForeignKey('users_info.id'), nullable=False)
    total_spent = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_spent': self.total_spent,
            'year': self.year
        }
