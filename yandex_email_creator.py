from tbselenium.tbdriver import TorBrowserDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import names
import string
import random
from pathlib import Path
import logging
import configparser
import psycopg2
from psycopg2 import extras
import os


def main():
    number_of_emails = 8
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    tor_path = "{}/tor-browser_en-US".format(Path.home())

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    db_connection = psycopg2.connect(host=config['database']['host'],
                                     dbname=config['database']['db_name'],
                                     user=config['database']['user'],
                                     password=config['database']['password'])
    try:
        with db_connection.cursor(cursor_factory=extras.RealDictCursor) as db_cursor:
            for i in range(number_of_emails):
                first_name = names.get_first_name()
                last_name = names.get_last_name()
                login = first_name.lower() + last_name.lower() + ''.join(random.choice(string.digits) for _ in range(5))
                email = "{}@yandex.com".format(login)
                password = ''.join(random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits + string.digits + string.ascii_lowercase) for _ in range(10))
                musician_surname = names.get_last_name()
                logging.info('Creating email %d out of %d - %s', i+1, number_of_emails, email)
                with db_connection:
                    db_cursor.execute("""
                        insert into yandex_email
                        (username, first_name, last_name, password_email, musician_surname, email)
                        values (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                                      (login, first_name, last_name, password, musician_surname, email))
                    logging.info('Will start Tor Browser')
                    with TorBrowserDriver(tor_path) as driver:
                        driver.get('https://passport.yandex.com/registration?from=mail&origin='
                                   'hostroot_homer_auth_L_com&retpath=https%3A%2F%2Fmail.yandex.com%2F')
                        first_name_input = driver.find_element_by_id('firstname')
                        first_name_input.send_keys(first_name)
                        last_name_input = driver.find_element_by_id('lastname')
                        last_name_input.send_keys(last_name)
                        login_input = driver.find_element_by_id('login')
                        login_input.send_keys(login)
                        password_input = driver.find_element_by_id('password')
                        password_input.send_keys(password)
                        confirm_password_input = driver.find_element_by_id('password_confirm')
                        confirm_password_input.send_keys(password)
                        link_no_phone = driver.find_element_by_css_selector('span.registration__pseudo-link.'
                                                                            'link_has-no-phone')
                        link_no_phone.click()
                        security_question_input = driver.find_element_by_id('hint_answer')
                        security_question_input.send_keys(musician_surname)
                        security_question_input.send_keys(Keys.TAB)
                        logging.info('Typed all info. Waiting for user to solve captcha...')
                        eula = WebDriverWait(driver, 100).until(
                            ec.visibility_of_element_located((By.CLASS_NAME, "t-eula-accept"))
                        )
                        accept = eula.find_element_by_css_selector('button.button2')
                        accept.click()
                        logging.info('Confirmed EULA. Waiting for redirecting to email page...')
                        WebDriverWait(driver, 200).until(
                            ec.presence_of_element_located((By.ID, "nb-3"))
                        )
                    logging.info('Closed Tor Browser')
                logging.info('Saved email %s on database', email)
    finally:
        db_connection.close()
        logging.info('Closed database connection')


if __name__ == '__main__':
    main()
