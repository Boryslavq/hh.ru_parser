import csv
import logging


def sort_vac():
    """Функция для сортировки только новых вакансий из сайта"""

    with open('csv_files/new_links.csv', 'r', encoding='utf-8') as file_1:
        new_data = list(csv.reader(file_1))
    with open('csv_files/old_links.csv', 'r', encoding='utf-8') as file_2:
        old_data = list(csv.reader(file_2))

    new_file = []
    for info in new_data:
        if info not in old_data:
            old_data.append(info)
            new_file.append(info)

    with open('csv_files/old_links.csv', 'w', newline='', encoding='utf-8') as file:
        write = csv.writer(file)
        for i in old_data:
            write.writerow(i)

    with open('csv_files/already_sorted.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in new_file:
            writer.writerow(i)

    logging.info('Отсортировано')
