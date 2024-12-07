import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

class ReviewTest(unittest.TestCase):
    
    def setUp(self):
        self.browser = webdriver.Chrome()  # Web driver swapped for Chrome
        self.browser.get('http://127.0.0.1:5000/signup')
        
    def tearDown(self):
        self.browser.quit()

    def test_signup(self): 
        userName = self.browser.find_element(By.ID, 'username')
        userName.send_keys('USER1')
        
        # Check if the username is already taken
        if self.browser.find_elements(By.TAG_NAME, 'div')[6].text == "That username is taken. Please choose a different one.":
            self.browser.quit()  # Skip the rest of the test

        email = self.browser.find_element(By.ID, 'email')
        email.send_keys('test@test.com')

        password = self.browser.find_element(By.ID, 'password')
        password.send_keys('123123123123')

        passwordConfirm = self.browser.find_element(By.ID, 'confirm_password')
        passwordConfirm.send_keys('123123123123')

        submitButton = self.browser.find_elements(By.TAG_NAME, 'button')[2]
        submitButton.click()

        page = self.browser.current_url
        self.assertEqual('http://127.0.0.1:5000/signup', page)

    def test_new_review(self):  # Movie ID: tt13623148
        
        #login 
        
        self.browser.get('http://127.0.0.1:5000/login')
        
        userName = self.browser.find_element(By.ID, 'username')
        userName.send_keys('USER1')

        password = self.browser.find_element(By.ID, 'password')
        password.send_keys('123123123123')

        submitButton = self.browser.find_elements(By.TAG_NAME, 'button')[2]
        submitButton.click()

        p = self.browser.find_element(By.TAG_NAME, 'p').text
        self.assertEqual("Welcome to the main page, USER1!", p)
        
        
        #------------------------------------------------------------------------------

        #check for review
        
        self.browser.get('http://127.0.0.1:5000/random')

        reviewButton = self.browser.find_element(By.CLASS_NAME, 'btn btn-primary')
        reviewButton.click()
        
        star = WebDriverWait(self.browser, 10).until(
        EC.element_to_be_clickable((By.TAG_NAME, 'span'))
        )
        ActionChains(self.browser).move_to_element(star).click().perform()

        comment = self.browser.find_element(By.ID, 'comment')
        comment.send_keys('test')

        submitButton = self.browser.find_elements(By.TAG_NAME, 'button')[9]
        submitButton.click()

        page = self.browser.current_url
        self.assertEqual('http://127.0.0.1:5000/media/movie/tt22060390', page)

        p = self.browser.find_element(By.ID, 'user_comment').text
        self.assertEqual('test', p)
  

if __name__ == '__main__':
    unittest.main()
