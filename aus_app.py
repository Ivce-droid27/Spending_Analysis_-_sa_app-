## aus_app - is Application for User Spending Analysis App
from flask import Flask, request, jsonify
from con_sqlalchemy import db
from user_info import User_info
from user_spent import Total, Average_spending_age
from sqlalchemy import func
import requests

# Create the Flask app instance
aus_app = Flask(__name__)

# Database configuration
aus_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
aus_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Telegram Bot Token (replace with your own token)
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'
# List of Telegram user chat IDs to send the results to
TELEGRAM_USER_IDS = ['USER_CHAT_ID_1', 'USER_CHAT_ID_2']

# Initialize the database with app
db.init_app(aus_app)

# Ensure app context when interacting with the database
with aus_app.app_context():
    db.create_all()
    print("Database and tables created")

def send_to_telegram(message, chat_id):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, data=payload)

@aus_app.route('/total_spent', methods=['GET'])
def get_total_spending():
    # !!! - the problem is in creating the table total_spent
    total_spending = Total.query.all()
    return jsonify([total.to_dict() for total in total_spending])


@aus_app.route('/users_info', methods=['GET'])
def get_users_info_s():
    users_ifons = User_info.query.all()
    return jsonify([user_info.to_dict() for user_info in users_ifons])


@aus_app.route('/average_spending_by_age', methods=['GET'])
def get_average_spending_by_age():
    # Join the 'Total' and 'User_info' tables
    results = db.session.query(
        func.avg(Total.total_spent).label('average_spent'),
        User_info.age
    ).join(
        User_info, Total.user_id == User_info.id
    ).group_by(
        User_info.age
    ).all()
    # # Define age ranges
    age_ranges = {
        "18-24": [],
        "25-30": [],
        "31-36": [],
        "37-47": [],
        ">47": []
    }
    # Classify data into age ranges
    for result in results:
        average_spent = result.average_spent
        age = result.age

        if 18 <= age <= 24:
            age_ranges["18-24"].append(average_spent)
        elif 25 <= age <= 30:
            age_ranges["25-30"].append(average_spent)
        elif 31 <= age <= 36:
            age_ranges["31-36"].append(average_spent)
        elif 37 <= age <= 47:
            age_ranges["37-47"].append(average_spent)
        elif age > 47:
            age_ranges[">47"].append(average_spent)

    # Calculate the average for each age range
    averages = {age_range: sum(spends) / len(spends) if spends else 0 for age_range, spends in age_ranges.items()}

    # Convert averages to a message string
    message = "\n".join([f"{age_range}: {average:.2f}" for age_range, average in averages.items()])

    # Send the message to specific Telegram users
    for user_id in TELEGRAM_USER_IDS:
        send_to_telegram(message, user_id)

    return jsonify(averages)



# 1. Retrieve Total Spending by User
@aus_app.route('/total_spent/<int:id>', methods=['GET'])
def get_total_spent_by_user(id):
    # total_spent = Total.query.get_or_404(id)
    #  Retrieves the total spending for a specific user based on their user ID.
    total_spent = Total.query.filter_by(user_id=id).first()

    if total_spent is None:
        return jsonify({'message': 'Total spending not found for this user'}), 404
    # user_id (integer): The unique user ID for the user.
    user_info = User_info.query.get_or_404(total_spent.user_id)
    result = {
        'name': user_info.nam,
        'email': user_info.email,
        'age': user_info.age,
        'pay_check': user_info.pay_check,
        'total_spent': total_spent.total_spent,
        'year': total_spent.year
    }
    # JSON object containing the user ID and total spending.
    return jsonify(result)


@aus_app.route('/users_info/<int:id>', methods=['GET'])
def get_user_info(id):
    user = User_info.query.get_or_404(id)
    return jsonify(user.to_dict())


@aus_app.route('/average_spending_by_age/<int:id>', methods=['GET'])
def get_average_spending_id(id):
    average = Average_spending_age.get_average_spending_by_age.query.get_or_404(id)
    return jsonify(average.to_dict())


@aus_app.route('/total_spent', methods=['POST'])
def create_totals_s():
    data = request.get_json()
    new_total = Total(total_spent=data['total_spent'], user_id=data['user_id'], name=data['name'], year=data['year'])
    db.session.add(new_total)
    db.session.commit()
    return jsonify(new_total.to_dict()), 201


@aus_app.route('/users_info', methods=['POST'])
def create_user_i():
    data = request.get_json()
    new_user = User_info(name=data['name'], email=data['email'], age=data['age'], pay_check=data['pay_check'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201


@aus_app.route('/average_spending_by_age', methods=['POST'])
def create_average_spending():
    data = request.get_json()

    for user_data in data:
        # Calculate the average spending or any other necessary field
        # Here, we assume you want to calculate total_spent based on user pay_check or some logic.
        total_spent = user_data.get('pay_check', 0)  # Example logic for total_spent

        # Creating the Average_spending_age object with the calculated total_spent
        new_average = Average_spending_age(
            user_id=user_data['user_id'],
            name=user_data['name'],
            age=user_data['age'],
            pay_check=user_data['pay_check'],
            total_spent=total_spent,  # Using the calculated or fetched total_spent
            average_spent=total_spent / 12,  # Example logic for average_spent (e.g., monthly average)
            year=2025  # Add the current year or any logic here
        )
        db.session.add(new_average)
        db.session.commit()
        return jsonify(new_average.to_dict())

@aus_app.route('/total_spent/<int:id>', methods=['PUT'])
def update_totals_s(id):
    data = request.get_json()
    total = Total.query.get_or_404(id)
    total.user_id = data.get('user_id', total.user_id)
    total.name = data.get('name', total.name)
    total.total_spent = data.get('total_spent', total.total_spent)
    total.year = data.get('year', total.year)
    db.session.commit()
    return jsonify(total.to_dict()), 200


@aus_app.route('/users_info/<int:user_id>', methods=['PUT'])
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
    average.user_id = data.get('user_id', average.user_id)
    average.name = data.get('name', average.name)
    average.age = data.get('age', average.age)
    average.pay_check = data.get('pay_check', average.pay_check)
    average.total_spent = data.get('total_spent', average.total_spent)
    average.year = data.get('year', average.year)
    db.session.commit()
    return jsonify(average.to_dict()), 200


@aus_app.route('/total_spent/<int:id>', methods=["DELETE"])
def delete_totals_s(id):
    total = Total.query.get_or_404(id)
    db.session.delete(total)
    db.session.commit()
    return jsonify({'message': 'Total spending deleted'})


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
