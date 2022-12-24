import unittest
from main import get_generation_dict_list
from selenium import webdriver

class BotTest(unittest.TestCase):

    def test_generation(self):
        self.driver = webdriver.Chrome()
        self.driver.get('https://auto.ru/cars/bmw/3er/all/')

        self.assertIsInstance(get_generation_dict_list(), list, 'This is not a list')


if __name__ == '__main__':
   unittest.main()
