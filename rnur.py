import sys
import os
from os.path import join, split
from datetime import datetime
import re

legal_types = ('VMZ', 'SNH', 'SUJ', 'CYT', 'GRF')

legal_projects = ('EN', 'UR', 'SU', 'VS')

replacer = {'_': ' ',
            '-': '',
            '!': '',
            '  ': ' ',
            '+': ' ',
            '032022': '0322',
            '042022': '0422',
            ' .': '.',
            'BZ ': 'VMZ ',
            ' BZ ': ' VMZ ',
            ' CX ': ' SNH',
            ' SH ': ' SNH ',
            ' SN ': ' SNH ',
            ' SNX ': ' SNH ',
            ' SUG ': ' SUJ ',
            ' SHN ': ' SNH ',
            ' GRF ': ' GX ',
            ' CIT ': ' CYT ',
            'SNH ZE.': 'SNH ZELENSKIY.',
            'SNH ZE ': 'SNH ZELENSKIY ',
            'VMZ ZE.': 'VMZ ZELENSKIY.',
            'VMZ ZE ': 'VMZ ZELENSKIY ',
            'ZELENSKY': 'ZELENSKIY',
            '.MP4.MP4': '.MP4',
            }


def name_prep(file_path):
    """
    Предварительная подготовка имени файла
    """
    new_name = os.path.basename(file_path).upper()
    new_name = re.sub(r"^\s+", "", new_name)
    for r in replacer:

        if r in new_name:
            new_name = new_name.replace(r, replacer[r])

    if new_name[:4] == "ARC ":
        new_name = new_name[4:]

    if new_name[:4] == "U 24":
        new_name = "U24" + new_name[4:]

    if new_name[:4] == "UA24":
        new_name = "U24" + new_name[4:]

    return new_name


def get_date(file_path):
    """
    Возвращает дату создания файла в формате ДДММГГ
    :param file_path:
    :return:
    """
    dates = []
    stat = os.stat(file_path)
    print("btime = ", datetime.fromtimestamp(stat.st_birthtime).strftime("%d%m%y"))
    dates.append(stat.st_birthtime)
    print("atime = ", datetime.fromtimestamp(stat.st_atime).strftime("%d%m%y"))
    dates.append(stat.st_atime)
    print("ctime = ", datetime.fromtimestamp(stat.st_ctime).strftime("%d%m%y"))
    dates.append(stat.st_ctime)
    print("mtime = ", datetime.fromtimestamp(stat.st_mtime).strftime("%d%m%y"))
    dates.append(stat.st_mtime)
    dates.sort()
    file_date = datetime.fromtimestamp(dates[0]).strftime("%d%m%y")
    return file_date


if __name__ == '__main__':
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = '/Volumes/Macintosh HD/Users/boba/Desktop/TESTUR'
    print(f"base_path: {base_path}")
    for f in os.listdir(base_path):
        path_file = join(base_path, f)

        if os.path.isdir(path_file):
            continue

        if f[0] == '.':
            continue

        date_file = get_date(path_file)  # храним дату создания файла

        print(date_file)
        print(f'ISX NAME: {f}')

        name_temp, ext_temp = name_prep(join(base_path, f)).split('.')  # храним отдельно имя и расширение файла
        del_parts = []  # список частей на удаление
        new_parts = ['U24', 'PROJECT', 'DATE', 'TYPE']  # список обязательных частей

        if re.match(r'V\s\d\d\s', name_temp):  # ищем файлы начинающиеся с V [0-9][0-9]
            name_temp = re.sub(r'V\s\d\d\s', '', name_temp)
            new_parts[1] = 'VS'

        name_parts = name_temp.split(' ')  # делим имя на части

        if len(name_parts) > 1:
            if name_parts[1] in legal_projects:  # проверяем второй блок (код проекта)
                new_parts[1] = name_parts[1]
                del_parts.append(name_parts[1])

        if re.match(r'\b\d\d\b', name_parts[0]):  # ищем файлы начинающиеся с "[0-9][0-9]"
            new_parts[1] = 'UR'
            del_parts.append(name_parts[0])

        if re.match(r'\bV\d\d\b', name_parts[0]):  # ищем файлы начинающиеся с "V[0-9][0-9]"
            new_parts[1] = 'VS'
            del_parts.append(name_parts[0])

        if re.match(r'\bD\b', name_parts[0]):  # ищем файлы начинающиеся с "D"
            new_parts[1] = 'UR'
            del_parts.append(name_parts[0])

        if re.match(r'\bV\b', name_parts[0]):  # ищем файлы начинающиеся с "V"
            new_parts[1] = 'VS'
            del_parts.append(name_parts[0])

        for part in name_parts:

            if part == 'U24':
                del_parts.append(part)
                continue

            if re.match(r'\bWSH\b', part):  # вариант обозначения военного щоденника
                new_parts[1] = 'VS'
                del_parts.append(part)
                continue

            if re.match(r'\d\d\d\d\d\d', part):  # поиск возможной даты
                print('part = ',
                      part if datetime.strptime(part, "%d%m%y") < datetime.strptime(date_file, "%d%m%y") else date_file)
                if new_parts[2] == 'DATE':
                    if datetime.strptime(part, "%d%m%y") < datetime.strptime(date_file, "%d%m%y"):
                        new_parts[2] = part
                    else:
                        new_parts[2] = date_file
                del_parts.append(part)
                continue

            if re.match(r'\d\d\d\d', part):  # поиск возможной даты
                try:
                    date_in_name = datetime.strptime(part + '22', "%d%m%y")
                except Exception as e:
                    print(part + '22', 'is not date', e)
                    continue

                print('part = ',
                      part if date_in_name < datetime.strptime(date_file, "%d%m%y") else date_file)
                if new_parts[2] == 'DATE':
                    if date_in_name < datetime.strptime(date_file, "%d%m%y"):
                        new_parts[2] = part + '22'
                    else:
                        new_parts[2] = date_file
                del_parts.append(part)
                continue

            if len(part) == 3 and part in legal_types:  # поиск возможного типа
                if new_parts[3] == 'TYPE':
                    new_parts[3] = part
                del_parts.append(part)
                continue

        if new_parts[2] == 'DATE':  # дата в имени не найдена берем из свойств файла
            new_parts[2] = date_file

        if new_parts[3] == 'TYPE':  # стандартный тип в имени не найден, ищем варианты
            if re.search(r'\bVMZ', name_temp):
                new_parts[3] = 'VMZ'
            if re.search(r'\bBZ\b', name_temp):
                new_parts[3] = 'VMZ'
            if re.search(r'\bOTRAG', name_temp):
                new_parts[3] = 'VMZ'
            if re.search(r'\bOTRAZHONKA', name_temp):
                new_parts[3] = 'VMZ'
            if re.search(r'\bDAIDJEST', name_temp):
                new_parts[3] = 'SUJ'
            if re.search(r'\bDAIDZHEST', name_temp):
                new_parts[3] = 'SUJ'
            if re.search(r'\bDIDGEST', name_temp):
                new_parts[3] = 'SUJ'
            if re.search(r'\bCYTATA', name_temp):
                new_parts[3] = 'SNH'
            if re.search(r'\bSN\b', name_temp):
                new_parts[3] = 'SNH'

        if new_parts[3] == 'TYPE':  # тип не найден
            new_parts.remove('TYPE')

        if new_parts[1] == 'PROJECT':  # код проекта не установлен
            # newparts.remove('PROJECT')
            new_parts[1] = 'UR'

        print(f'delparts : {del_parts}')
        print(f'nameparts: {name_parts}')

        for part in del_parts:  # удаляем из списка частей обработанные
            name_parts.remove(part)

        new_parts += name_parts  # к шаблонной части добавляем специфическую
        new_name = ''

        for x in range(len(new_parts)):  # собираем новое имя
            if x == len(new_parts) - 1:
                new_name += new_parts[x] + '.'
            else:
                new_name += new_parts[x] + ' '
        new_name += ext_temp  # возвращаем расширение файла
        print(f"NEW NAME: {new_name}\n")
        os.rename(path_file, join(split(path_file)[0], new_name))  # переименовываем
