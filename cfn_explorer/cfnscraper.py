from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException

class Logger:

    URL = "https://www.streetfighter.com/6/buckler/auth/loginep?redirect_url=/"

    dropdown_country = "US"
    dropdown_Day     = "1"
    dropdown_Year    = "2000"
    dropdown_Month   = "1"

    def __init__(self, email: str, password: str):
        self.email    = email
        self.password = password
        self.driver   = webdriver.Chrome()

    def cfn_login(self):
        """Login on CFN by cheking in capcom id to retrieve the SF6 buckler's cookie

        :return: a token value
        """
        self.driver.get(self.URL)

        exempt_wait_erros = [NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException]
        wait = WebDriverWait(self.driver, 10, ignored_exceptions=exempt_wait_erros)

        #Capcom id age check
        wait.until(lambda _: (self.driver.find_element(By.ID, "country")).is_displayed())

        self.__dropdown_fill("country"   , self.dropdown_country)
        self.__dropdown_fill("birthDay"  , self.dropdown_Day    )
        self.__dropdown_fill("birthYear" , self.dropdown_Year   )
        self.__dropdown_fill("birthMonth", self.dropdown_Month  ) 

        self.driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonDecline").click()
        self.driver.find_element(By.NAME, "submit").click()     

        #Capcom id authentication page
        wait.until(lambda _: (self.driver.find_element(By.NAME, "email")).is_displayed())

        self.driver.find_element(By.NAME, "email"   ).send_keys(self.email   )
        self.driver.find_element(By.NAME, "password").send_keys(self.password)

        self.driver.find_element(By.NAME, "submit").click()

        wait.until(lambda _: (self.driver.find_element(By.ID, "__next")).is_displayed())

        return self.driver.get_cookie("buckler_id").get("value")
        
    def __dropdown_fill(self, element:str, value:str):
        """fill a dropdown element

        :Args:
        - element: web element ID
        - value: value to be selected in the element
        """
        dropdown = self.driver.find_element(By.ID, element)
        Select(dropdown).select_by_value(value)
