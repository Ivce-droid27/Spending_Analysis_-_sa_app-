## aus_app - is Application for User Spending Analysis App
from flask import Flask, request, jsonify, render_template
from con_sqlalchemy import db, voucher_collection
from models import User_info, Total
from sqlalchemy import func
import requests


# Create the Flask app instance
aus_app = Flask(__name__)

# Database configuration
aus_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///C:/Users/ivo/PycharmProjects/PythonVRE/instance/users_vouchers.db'
aus_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with app
db.init_app(aus_app)

# Ensure app context when interacting with the database
with aus_app.app_context():
    db.create_all()

# Route for the homepage / # 2. Calculate Average Spending by Age Ranges
@aus_app.route('/')
def home():
    results = db.session.query(
        func.avg(Total.money_spent).label('average_spent'), User_info.age
    ).join(User_info, Total.user_id == User_info.user_id).group_by(User_info.age).all()

    # Define age ranges and categorize spending
    averages = {
        "18-24": [],
        "25-30": [],
        "31-36": [],
        "37-47": [],
        ">47": []
    }

    # Assign each result to its respective age range
    for result in results:
        age = result.age
        average_spent = result.average_spent

        if 18 <= age <= 24:
            averages["18-24"].append(average_spent)
        elif 25 <= age <= 30:
            averages["25-30"].append(average_spent)
        elif 31 <= age <= 36:
            averages["31-36"].append(average_spent)
        elif 37 <= age <= 47:
            averages["37-47"].append(average_spent)
        elif age > 47:
            averages[">47"].append(average_spent)

    # Calculate the average spending for each age range
    averages = {age_range: sum(spends) / len(spends) if spends else 0 for age_range, spends in averages.items()}

    # Send data to Telegram bot
    bot_token = '8164159308:AAG7mV-JfZUKSECJ7lOHC0I7dl3spZuCPqI'  # Твојот Telegram бот токен
    chat_id = '8011204510'  # Твојот Telegram chat ID

    message = "Average Spending by Age Range:\n"
    for age_range, avg in averages.items():
        message += f"{age_range}: ${avg:.2f}\n"

    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    # Sending the message
    requests.get(telegram_url, params=params)

    # Врати ја HTML страницата со податоци
    return render_template('Home_page.html', averages=averages)

@aus_app.route('/total_spent', methods=['GET'])
def get_money_spending():
    money_spending = Total.query.all()
    return jsonify([money.to_dict() for money in money_spending])


@aus_app.route('/users_info', methods=['GET'])
def get_users_info_s():
    users_infos = User_info.query.all()
    return jsonify([user_info.to_dict() for user_info in users_infos])


# 1. Retrieve Total Spending by User
@aus_app.route('/total_spent/<int:id>', methods=['GET'])
def get_total_spent_by_user(id):
    #  Retrieves the total spending for a specific user based on their user ID.
    total_spent = Total.query.filter_by(user_id=id).first()

    if total_spent is None:
        return jsonify({'message': 'Total spending not found for this user'}), 404
    # user_id (integer): The unique user ID for the user.
    user_info = User_info.query.get_or_404(total_spent.user_id.id)
    result = {
    'name': user_info.name,
    'email': user_info.email,
    'age': user_info.age,
    'money_spent': total_spent.money_spent,
    'year': total_spent.year
    }
    # JSON object containing the user ID and total spending.
    return jsonify(result, user_info.name)


@aus_app.route('/users_info/<int:id>', methods=['GET'])
def get_user_info(id):
    user = User_info.query.get_or_404(id)
    return jsonify(user.to_dict())


@aus_app.route('/total_spent', methods=['POST'])
def create_totals_s():
    data = request.get_json()
    new_money = Total(money_spent=data['money_spent'], user_id=data['user_id'], year=data['year'])
    db.session.add(new_money)
    db.session.commit()
    return jsonify(new_money.to_dict()), 201


@aus_app.route('/users_info', methods=['POST'])
def create_user_i():
    data = request.get_json()
    # new_user = User_info(name=data['name'], email=data['email'], age=data['age'], pay_check=data['pay_check'])
    new_user = User_info(name=data['name'], email=data['email'], age=data['age'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201


# 2. Write user data to MongoDB
@aus_app.route('/write_to_mongodb', methods=['POST'])
def write_to_mongodb():
    try:
        # Get JSON data from the POST request
        data = request.get_json()

        # Validate the input data (check if required fields are present)
        if 'user_id' not in data or 'total_spent' not in data:
            return jsonify({'error': 'Missing user_id or total_spent in request data'}), 400

        user_id = data['user_id']
        total_spent = data['total_spent']

        # Check if total_spending exceeds the threshold (e.g., 1000)
        if total_spent <= 1000:
            return jsonify({'error': 'Total spending must exceed 1000'}), 400

        # Prepare the data for MongoDB
        user_data = {
            'user_id': user_id,
            'total_spending': total_spent
        }

        # Insert data into MongoDB collection
        result = voucher_collection.insert_one(user_data)

        # Respond with success message and status code 201 Created
        return jsonify({
            'message': 'User data successfully inserted into MongoDB',
            'data': {
                'user_id': user_id,
                'total_spend': total_spent,
                'mongo_id': str(result.inserted_id)  # Ensure the ObjectId is converted to string
            }
        }), 201

    except Exception as e:
        # Handle unexpected errors
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@aus_app.route('/users_info/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User_info.query.get_or_404(user_id)
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.age = data.get('age', user.age)
    db.session.commit()
    return jsonify(user.to_dict()), 200


if __name__ == "__main__":
    aus_app.run(debug=True)
