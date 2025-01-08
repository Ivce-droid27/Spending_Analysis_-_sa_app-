## aus_app - is Application for User Spending Analysis App
from flask import Flask, request, jsonify
from con_sqlalchemy import db
from user_info import User_info
from user_spent import Total

# Create the Flask app instance
aus_app = Flask(__name__)

# Database configuration
aus_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
aus_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with app
db.init_app(aus_app)

# Ensure app context when interacting with the database
with aus_app.app_context():
    # Create the tables at startup
    db.create_all()


@aus_app.route('/total_spent', methods=['GET'])
def get_totals():
    totals = Total.query.all()
    return jsonify([total.to_dict() for total in totals])


@aus_app.route('/users_info', methods=['GET'])
def get_users_info_s():
    users_ifons = User_info.query.all()
    return jsonify([user_info.to_dict() for user_info in users_ifons])


# # 2. Calculate Average Spending by Age Ranges
# @aus_app.route('/average_spending_by_age', methods=['GET'])


# 1. Retrieve Total Spending by User
@aus_app.route('/total_spent/<int:user_id>', methods=['GET'])
def get_total_spent_by_user(id):
    total_spent = Total.query.get_or_404(id)
    user_info = User_info.query.get_or_404(total_spent.user_id)
    total_spent_dict = total_spent.to_dict()
    user_info_dict = {
        'name': user_info.name,
        'email': user_info.email,
        'age': user_info.age
    }
    total_spent_dict['user_info'] = user_info_dict
    return jsonify(total_spent_dict)


@aus_app.route('/users_info/<int:id>', methods=['GET'])
def get_user_info(id):
    user = User_info.query.get_or_404(id)
    return jsonify(user.to_dict())


@aus_app.route('/total_spent', methods=['POST'])
def create_totals_s():
    data = request.get_json()
    new_total = Total(total_spent=data['total_spent'], user_id=data['user_id'])
    db.session.add(new_total)
    db.session.commit()
    return jsonify(new_total.to_dict()), 201


@aus_app.route('/user_info', methods=['POST'])
def create_user_i():
    data = request.get_json()
    new_user = User_info(name=data['name'], email=data['email'], age=data['age'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201


@aus_app.route('/total_spent/<int:id>', methods=['PUT'])
def update_totals_s(id):
    data = request.get_json()
    total = Total.query.get_or_404(id)
    total.total_spent = data.get('total_spent', total.total_spent)
    total.user_id = data.get('user_id', total.user_id)  # Corrected assignment
    db.session.commit()
    return jsonify(total.to_dict())


@aus_app.route('/user_info/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User_info.query.get_or_404(id)
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.age = data.get('age', user.age)
    db.session.commit()
    return jsonify(user.to_dict())


#
@aus_app.route('/total_spent/<int:id>', methods=["DELETE"])
def delete_totals_s(id):
    total = Total.query.get_or_404(id)
    db.session.delete(total)
    db.session.commit()
    return jsonify({'message':'Total spending deleted'})


@aus_app.route('/users_info/<int:id>', methods=["DELETE"])
def delete_users_info(id):
    user = User_info.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message':'Users info deleted'})


if __name__ == "__main__":
    aus_app.run(debug=True)