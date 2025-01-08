from con_sqlalchemy import db

class Total(db.Model):
    __tablename__ = "total_spent"

    id = db.Column(db.Integer, primary_key=True)
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


# class Average_spending_age(db.Model):
#     __tablename__ = "average_spending_by_age"
#
#     id = db.Column(db.Integer, primary_key=True)
#     average_spent = db.Column(db.Float, nullable=False)
#     total_id = db.Column(db.Integer,  db.ForeignKey('total_spent.id'), nullable=False)


