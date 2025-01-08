from con_sqlalchemy import db

class Total(db.Model):
    __tablename__ = "total_spent"

    id = db.Column(db.Integer, primary_key=True) # autoincrement=True
    total_spent = db.Column(db.Float, nullable=False)
    year = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer,  db.ForeignKey('users_info.id'), nullable=False)


    def to_dict(self):
        return {
            'id': self.id,
            'total_spent': self.total_spent,
            'year': self.year,
            'user_id': self.user_id
        }


class Average_spending_age(db.Model):
    __tablename__ = "average_spending_by_age"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_info.id'), nullable=False)
    name = db.Column(db.String(20), db.ForeignKey('users_info.id'), nullable=False)
    age = db.Column(db.Integer, db.ForeignKey('users_info.id'), nullable=False)
    pay_check = db.Column(db.Integer, db.ForeignKey('users_info.id'), nullable=False, default=0)
    total_spent = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    average_spent = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'total_spent': self.total_spent,
            'year': self.year,
            'average_spent': self.average_spent
        }
