import logging
import time

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
import csv
import multiprocessing as mp
import os
import glob
import csv
from xlsxwriter.workbook import Workbook


def get_page(reference):
    # функция для того что бы узнать количество страниц для той или иной вакансии
    import requests
    from bs4 import BeautifulSoup
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


def main(data):
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    options = webdriver.ChromeOptions()

    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Chrome/95.0.4638.69 Safari/537.36')

    options.add_argument('--disable-blink-features=AutomationControlled')
    options.headless = True

    driver = webdriver.Chrome(
        options=options,
        desired_capabilities=caps)

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

    driver.quit()


if __name__ == "__main__":
    from parse_vacansies import parse_vac

    links = list(csv.reader(open('industries.csv', 'r', encoding='utf-8'), delimiter=','))
    pool = mp.Pool(processes=6)
    pool.map(main, [links[0:10], links[10:20], links[20:25], links[25:34], links[34:36], links[36:]])
    print('Ссылки спаршены')
    import csv

    new_data = list(csv.reader(open('new_links.csv', 'r', encoding='utf-8')))
    old_data = list(csv.reader(open('old_links.csv', 'r', encoding='utf-8')))

    new_file = []
    for info in new_data:
        if info not in old_data:
            old_data.append(info)
            new_file.append(info)

    with open('old_links.csv', 'w', newline='', encoding='utf-8') as file:
        write = csv.writer(file)
        for i in old_data:
            write.writerow(i)

    with open('already_sorted.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in new_file:
            writer.writerow(i)

    print('Отсортировано')

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
    for csvfile in glob.glob(os.path.join('.', 'vacancies.csv')):
        workbook = Workbook(csvfile[:-4] + '.xlsx')
        worksheet = workbook.add_worksheet()
        with open(csvfile, 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()

    print('Парсинг окончен')

    q = open("new_links.csv", "w")
    q.truncate()
    q.close()