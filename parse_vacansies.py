import csv

from selenium.webdriver import DesiredCapabilities

import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys


def parse_vac(data: list):
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    options = webdriver.ChromeOptions()

    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36')

    options.add_argument('--disable-blink-features=AutomationControlled')
    options.headless = True

    driver = webdriver.Chrome(r'C:\Users\borys\.wdm\drivers\chromedriver\win32\95.0.4638.54\chromedriver.exe',
                              options=options,
                              desired_capabilities=caps)
    driver.get('https://hh.ru/account/login?backurl=%2Fapplicant%2Fresumes%2Fnew')
    time.sleep(3)
    input = driver.find_element_by_xpath("//input[@data-qa='account-signup-email']")
    input.send_keys('email')
    driver.find_element_by_xpath('//span[@class="bloko-link-switch"]').click()
    input2 = driver.find_element_by_xpath('//input[@class="bloko-input bloko-input_password"]')
    input2.send_keys('password')
    input2.send_keys(Keys.ENTER)
    for element in data:
        try:
            driver.get(element[0])
            time.sleep(2)
        except Exception:
            pass

        try:
            driver.find_element_by_css_selector("span.bloko-link-switch").click()
            time.sleep(1)
            phone = driver.find_element_by_class_name("vacancy-contacts__phone-desktop").text
            print(phone)
        except:
            phone = False

        if phone:
            title = driver.find_element_by_tag_name("h1").text
            title = f'{title}'
            salary = driver.find_element_by_class_name('vacancy-salary').text
            try:
                description = driver.find_element_by_xpath('//div[@data-qa="vacancy-description"]').text
                description = f'{description}'
            except NoSuchElementException:
                description = driver.find_element_by_class_name('g-user-content').text
                description = f'{description}'
            try:
                company_name = driver.find_element_by_class_name('vacancy-company-name').text
                company_name = f'{company_name}'

            except NoSuchElementException:
                company_name = f'Не указано'
            try:
                name_of_contact = driver.find_element_by_xpath('//p[@data-qa="vacancy-contacts__fio"]').text
            except NoSuchElementException:
                name_of_contact = 'Не указано'
            try:
                email = driver.find_element_by_xpath('//a[@data-qa="vacancy-contacts__email"]').text
            except NoSuchElementException:
                email = "Не указан"
            try:
                city = driver.find_element_by_xpath("//span[@data-qa='vacancy-view-raw-address']").text
            except NoSuchElementException:
                city = driver.find_element_by_xpath("//p[@data-qa='vacancy-view-location']").text
            try:
                all_skill = " "
                skills = driver.find_elements_by_xpath(
                    "//span[@class='bloko-tag__section bloko-tag__section_text']")
                for skill in skills:
                    all_skill += f'{skill.text};'
            except:
                all_skill = "Не указано"

            with open('vacancies.csv', 'a', encoding='utf-8') as f:
                writers = csv.writer(f, delimiter=',')
                writers.writerow(
                    [element[1], element[0], title, salary, company_name, city, description, all_skill, name_of_contact,
                     phone,
                     email])
    driver.quit()
