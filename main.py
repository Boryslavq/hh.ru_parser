import csv
import glob
import logging
import multiprocessing as mp
import os
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from xlsxwriter.workbook import Workbook

from parse_vacancies import parse_vac
from sorted_vacancies import sort_vac


def create_driver():
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    options = webdriver.ChromeOptions()

    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Chrome/95.0.4638.69 Safari/537.36')

    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(
        options=options,
        desired_capabilities=caps)
    return driver


def clean_file():
    """Очистка файла"""

    with open('new_links.csv', 'w') as f:
        f.truncate()
    logging.info('Файл очищен')


def vacancies_processes():
    """Создание процессов для парсинга вакансий"""
    logging.info('Парсинг вакансий начался')
    pool = mp.Pool(processes=6)

    data = list(csv.reader(open('already_sorted.csv', 'r', encoding='utf-8'), delimiter=','))
    new_separator = round(len(data) / 6)
    with open('vacancies.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(
            ['Отрасль компании', 'Ссылка', 'Название вакансии', 'Зарплата', 'Компания', 'Город', 'Описание вакансии',
             'Навыки',
             'Имя', 'Телефон', 'Email'])
    pool.map(parse_vac,
             [data[0:new_separator], data[new_separator:new_separator * 2],
              data[new_separator * 2:new_separator * 3],
              data[new_separator * 3:new_separator * 4],
              data[new_separator * 4:new_separator * 5],
              data[new_separator * 5:]])
    pool.close()
    pool.join()
    logging.info('Парсинг окончен')


def link_processes():
    """Создание процессов для функции extract_links"""
    logging.info('Парсинг ссылок начался')

    links = list(csv.reader(open('industries.csv', 'r', encoding='utf-8'), delimiter=','))
    pool = mp.Pool(processes=6)
    pool.map(extract_links, [links[0:10], links[10:20], links[20:25], links[25:34], links[34:36], links[36:]])
    logging.info('Ссылки спаршены')


def from_csv_to_xlsx():
    """Конвертация с csv в xlsx"""
    logging.info('Начало конвертации')

    for csvfile in glob.glob(os.path.join('.', 'vacancies.csv')):
        workbook = Workbook(csvfile[:-4] + '.xlsx')
        worksheet = workbook.add_worksheet()
        with open(csvfile, 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()
    logging.info('Конвертация прошла успешно')


def get_page(reference):
    """Функция для того что бы узнать количество страниц для той или иной вакансии"""

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
    }
    r = requests.get(reference, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    block = soup.find('span', class_='bloko-button-group')
    if block is not None:
        pages = block.find_all('a', class_='bloko-button')
        if pages is not None:
            return int(pages[-2].get_text())
    else:
        return 1


def extract_links(data):
    """ Функция для извлечения всех ссылок со страницы"""
    driver = create_driver()
    mylist = []
    count1 = 0
    for reference in data:
        count = get_page(reference[0])
        time.sleep(1)
        count1 += 1
        for count_of_pages in range(0, count):
            driver.get(reference[0] + f'&page={count_of_pages}')
            time.sleep(1)
            sites = driver.find_elements_by_class_name(
                'bloko-link')
            for urls in sites:
                html = urls.get_attribute('href')
                try:
                    if html.startswith('https://hh.ru/vacancy'):  # фильтр для вакансий
                        mylist.append([html, reference[1]])
                except AttributeError:
                    pass
    with open('new_links.csv', 'a', newline='', encoding='utf-8') as f:  # записываем все собранные сылки в лс
        writer = csv.writer(f, delimiter=',')
        for item in mylist:
            writer.writerow(item)
    logging.info('Ссылки собраны')
    driver.quit()


def main():
    logging.info('Парсинг начался')
    link_processes()
    sort_vac()
    from_csv_to_xlsx()
    vacancies_processes()
    clean_file()
    logging.info('Парсинг окончен')


if __name__ == "__main__":
    main()
