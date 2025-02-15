import unittest
import requests
from pymongo import MongoClient



# Тестови за веб-страниците
class TestWebsite(unittest.TestCase):

    def test_user_info_status(self):
        """Тестријање на user_info стана дали ќе врати 200"""
        response = requests.get("http://127.0.0.1:5000/users_info")
        self.assertEquals(response.status_code, 200, "user_info станица не враќа статус 200")

    def test_total_spent_status(self):
        """Тестријање на total_spent стана дали ќе врати 200"""
        response = requests.get("http://127.0.0.1:5000/total_spent")
        self.assertEquals(response.status_code, 200, "total_spent станица не враќа статус 200")

    def test_average_spending_by_age_status(self):
        """Тестријање на average_spending_by_age стана дали ќе врати 200"""
        response = requests.get("http://127.0.0.1:5000/average_spending_by_age")
        self.assertEquals(response.status_code, 200, "average_spending_by_age станица не враќа статус 200")



# Тестови за MongoDB
class TestMongoDB(unittest.TestCase):

    db = None
    client = None

    @classmethod
    def setUpClass(cls):
        """Конектирање со MongoDB"""
        cls.client = MongoClient("mongodb://localhost:27017/")
        cls.db = cls.client["mydatabase"]
        cls.collection = cls.db["users"]

    def setUp(self):
        """Чистење на базата на податоци пред секој тест"""
        self.collection.delete_many({})

    def test_insert_data(self):
        """Тестирање дали податоците се успешно внесени во MongoDB"""
        user_data = {
            "name": "John Doe",
            "email": "john.doe@example.com"
        }
        insert_result = self.collection.insert_one(user_data)
        self.assertIsNotNone(insert_result.inserted_id, "Документот не е внесен во MongoDB")

        result = self.collection.find_one({"email": "john.doe@example.com"})
        self.assertIsNotNone(result, "Не беа пронајдени податоци во базата")
        self.assertEqual(result["name"], "John Doe", "Името не се совпадна")
        self.assertEqual(result["email"], "john.doe@example.com", "Електронската пошта не се совпадна")

    def tearDown(self):
        """Чистење на базата по секој тест"""
        self.collection.delete_many({})

    @classmethod
    def tearDownClass(cls):
        """Затворање на конекцијата со MongoDB по сите тестови"""
        cls.client.close()


if __name__ == '__main__':
    unittest.main()