from con_sqlalchemy import db

class User_info(db.Model):
    __tablename__ = "user_info"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(65), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'age': self.age
        }


class Total(db.Model):
    __tablename__ = "user_spending"

    user_id = db.Column(db.Integer,  db.ForeignKey('user_info.user_id'), primary_key=True)
    money_spent = db.Column(db.Float, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'total_spent': self.money_spent,
            'year': self.year
        }
