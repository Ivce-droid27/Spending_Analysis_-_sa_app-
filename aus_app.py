## aus_app - is Application for User Spending Analysis App
from flask import Flask, request, jsonify
from con_sqlalchemy import db
from user_info import User_info
from user_spent import Total, Average_spending_age
from sqlalchemy import func

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


# 2. Calculate Average Spending by Age Ranges
@aus_app.route('/average_spending_by_age', methods=['GET'])
def get_average_spending_age():
    # Define specific age ranges as requested
    age_range = [(18,24), (25,30), (31,36), (37,47), (48,100)]
    # Store the results
    results = []

    for age_min, age_max in age_range:
        # Get the users within the age range
        users_in_range = User_info.query.filter(User_info.age.between(age_min, age_max)).all()

        if users_in_range :
            # Get the total spending for the users within this age range
            total_spent_in_range = db.session.query(func.sum(Total.total_spent)).join(Total).filter(
                Total.user_id.in_([user.id for user in users_in_range ])
            ).scalar() or 0

            # Calculate the average spending in this age range
            average_spending = total_spent_in_range / len(users_in_range) if users_in_range else 0
        else:
            average_spending = 0

        # Append the result for this age range
        results.append({
            'age_range': f'{age_min}-{age_max}' if age_max != 100 else f'{age_min}+',
            'average_spending': round(average_spending, 2)
        })

    return jsonify(results)


# 1. Retrieve Total Spending by User
@aus_app.route('/total_spent/<int:user_id>', methods=['GET'])
def get_total_spent_by_user(user_id):
    # Retrieve the total spending record for the specified user
    total_spent = Total.query.filter_by(user_id=user_id).first()

    # If no total is found for the user, return a 404 response
    if total_spent is None:
        return jsonify({'message': 'Total spending not found for this user'}), 404

    # Retrieve user info from the 'User_info' table
    user_info = User_info.query.get_or_404(total_spent.user_id)

    # Create a dictionary with user information and their total spending
    result = {
        'name': user_info.name,
        'email': user_info.email,
        'age': user_info.age
    }
    # Return the JSON response
    return jsonify(result)


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


@aus_app.route('/user_info/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User_info.query.get_or_404(user_id)
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.age = data.get('age', user.age)
    db.session.commit()
    return jsonify(user.to_dict()), 200


@aus_app.route('/average_spending_by_age/<int:id>', methods=['PUT'])
def update_average(id):
    data = request.get_json()
    average = Average_spending_age.query.get_or_404(id)
    average.average_spent = data.get('average_spent', average.average_spent)
    db.session.commit()
    return jsonify(average.to_dict()), 200


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

@aus_app.route('/average_spending_by_age/<int:id>', methods=["DELETE"])
def delete_average_s_a(id):
    average = Average_spending_age.query.get_or_404(id)
    db.session.delete(average)
    db.session.commit()
    return jsonify({'message':'Average info deleted'})


if __name__ == "__main__":
    aus_app.run(debug=True)
