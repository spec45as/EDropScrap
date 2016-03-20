from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from lxml import html


class PageCouldntBeLoadedException(LookupError):
    '''raise when our page couldn't be loaded!'''


class NoItemsException(LookupError):
    '''raise when current user doesn't have any items'''


class SeleniumLoader():
    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.wait = WebDriverWait(self.driver, 12)

    def loadCategories(self):
        try:
            self.driver.get("http://www.easydrop.ru/")

            try:
                self.wait.until(lambda driver: driver.find_element_by_class_name('collection'))
            except:
                raise PageCouldntBeLoadedException()

            final = html.fragment_fromstring(self.driver.page_source, 'root')
            return final
        except:
            print('I could not load the page')
            return None


    def loadCountURL(self):
        try:
            self.driver.get("http://www.easydrop.ru/user/1")

            try:
                self.wait.until(lambda driver: driver.find_element_by_id('drops'))
            except:
                raise PageCouldntBeLoadedException()

            final = html.fragment_fromstring(self.driver.page_source, 'root')
            return final
        except:
            print('I could not load the page')
            return None

    def loadUserInventoryURL(self, url):
        self.driver.get(url)

        try:
            self.wait.until(lambda driver: driver.find_element_by_id('drops'))
        except:
            print('I could not load the page')
            raise PageCouldntBeLoadedException()
            return None

        # print(self.driver.find_element_by_id('drops').find_elements_by_xpath(".//p")[0].text)

        try:
            self.wait.until(lambda driver: driver.find_element_by_class_name('drop-image'))
        except:
            raise NoItemsException()
            return None

        final = html.fragment_fromstring(self.driver.page_source, 'root')
        return final


    def quit(self):
        self.driver.quit()