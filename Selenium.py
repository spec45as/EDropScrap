from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from lxml import html


class PageCouldntBeLoadedException(LookupError):
    '''raise when our page couldn't be loaded!'''


class NoItemsException(LookupError):
    '''raise when current user doesn't have any items'''


class SeleniumLoader():
    def __init__(self, baseURL, isDota):
        self.isDota = isDota
        self.baseURL = baseURL

        options = []
        # options.append('--proxy={}:{}'.format(host,port))
        # options.append('--proxy-type=http')
        options.append('--load-images=false')
        options.append('--disk-cache=false')
        self.driver = webdriver.PhantomJS(service_args=options)
        self.wait = WebDriverWait(self.driver, 5)
        self.waitForItems = WebDriverWait(self.driver, 1)


    def loadCategories(self):
        try:
            self.driver.get(self.baseURL)

            try:
                if self.isDota:
                    self.wait.until(lambda driver: driver.find_element_by_class_name('item'))
                else:
                    self.wait.until(lambda driver: driver.find_element_by_class_name('collection'))
            except:
                raise PageCouldntBeLoadedException()

            final = html.fragment_fromstring(self.driver.page_source, 'root')
            return final
        except:
            print('I could not load category page')
            return None


    def loadCountURL(self):
        try:
            self.driver.get(self.baseURL + "/user/1")

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
            self.waitForItems.until(lambda driver: driver.find_element_by_class_name('drop-image'))
        except:
            raise NoItemsException()
            return None

        final = html.fragment_fromstring(self.driver.page_source, 'root')
        return final


    def quit(self):
        self.driver.quit()
