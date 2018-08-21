import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from eksam.testing import server_running

TIME_TO_RESPOND = 2


def test_normal_submission():
    options = webdriver.ChromeOptions()
    options.binary_location = '/usr/bin/google-chrome'
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')
    browser = webdriver.Chrome(chrome_options=options)
    browser.get('http://127.0.0.1:5000/1/')
    id_field = browser.find_element_by_id('student_id')
    id_field.clear()
    id_field.send_keys('1111')
    id_field.send_keys(Keys.RETURN)
    statements = browser.find_elements(By.TAG_NAME, 'label')
    print('Checking that there are 8 statements')
    assert len(statements) == 8
    print('Checking that we see chapter 2')
    for statement in statements:
        # This should be chapter 2
        assert not statement.text == 'A square has five corners'
    time.sleep(TIME_TO_RESPOND + .5)  # Allow half a second for loading
    statements = browser.find_elements(By.TAG_NAME, 'label')
    print('Post submission: No more statements')
    assert len(statements) == 0
    body = browser.find_element(By.TAG_NAME, 'body')
    print('Post submission: Thank you message')
    assert 'Thank you' in body.text

    # No backward
    browser.back()
    time.sleep(TIME_TO_RESPOND + .5)

    body = browser.find_element(By.TAG_NAME, 'body')
    print('Resubmission gives unauthorized')
    assert 'Unauthorized' in body.text

    browser.close()
    browser.stop_client()
    print('All tests passed')


with server_running(TIME_TO_RESPOND):
    test_normal_submission()
