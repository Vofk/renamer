import sys
import os
from os.path import join, split
from datetime import datetime
import re

legaltypes = ('VMZ', 'SNH', 'SUJ', 'CYT', 'GRF')

legalprojects = ('EN', 'UR', 'SU', 'VS')

replacer = {'_': ' ',
            '-': '',
            '!': '',
            '  ': ' ',
            '+': ' ',
            '032022': '0322',
            '042022': '0422',
            ' .': '.',
            'BZ ': 'VMZ ',
            'SH ': 'SNH ',
            'SN ': 'SNH ',
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
#  0     1    2     3
# U24 190322 SNH OBSTRILY AUDIO.mp4
#  0   1      2    3
# U24 DDMMYY TYP NAME

# Предварительная подготовка имени файла


def nameprep(file_path):
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

# Возвращает дату создания файла в формате ДДММГГ


def getdate(file_path):
    stat = os.stat(file_path)
    print("btime = ", datetime.fromtimestamp(stat.st_birthtime).strftime("%d%m%y"))
    print("atime = ", datetime.fromtimestamp(stat.st_atime).strftime("%d%m%y"))
    print("ctime = ", datetime.fromtimestamp(stat.st_ctime).strftime("%d%m%y"))
    print("mtime = ", datetime.fromtimestamp(stat.st_mtime).strftime("%d%m%y"))
    filedate = datetime.fromtimestamp(stat.st_birthtime).strftime("%d%m%y")
    return filedate


if __name__ == '__main__':
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = '/Volumes/Macintosh HD/Users/boba/Desktop/TESTUR'
    print(f"base_path: {base_path}")
    for f in os.listdir(base_path):
        pathfile = join(base_path, f)

        if os.path.isdir(pathfile):
            continue

        if f[0] == '.':
            continue

        datefile = getdate(pathfile)                                    # храним дату создания файла

        print(datefile)
        print(f'ISX NAME: {f}')

        nametemp, exttemp = nameprep(join(base_path, f)).split('.')     # храним отдельно имя и расширение файла
        delparts = []                                                   # список частей на удаление
        newparts = ['U24', 'PROJECT', 'DATE', 'TYPE']                   # список обязательных частей

        if re.match(r'V\s\d\d\s', nametemp):                            # ищем файлы начинающиеся с V [0-9][0-9]
            nametemp = re.sub(r'V\s\d\d\s', '', nametemp)
            newparts[1] = 'VS'

        nameparts = nametemp.split(' ')                                 # делим имя на части

        if nameparts[1] in legalprojects:                               # проверяем второй блок (код проекта)
            newparts[1] = nameparts[1]
            delparts.append(nameparts[1])

        if re.match(r'\b\d\d\b', nameparts[0]):                             # ищем файлы начинающиеся с "[0-9][0-9]"
            newparts[1] = 'UR'
            delparts.append(nameparts[0])

        if re.match(r'\bV\d\d\b', nameparts[0]):                            # ищем файлы начинающиеся с "V[0-9][0-9]"
            newparts[1] = 'VS'
            delparts.append(nameparts[0])

        for part in nameparts:

            if part == 'U24':
                delparts.append(part)
                continue

            # if re.match(r'\b\d{2}\b', part):                          # две цифры могут означать порядковый номер
            #     newparts[1] = 'UR'
            #     delparts.append(part)
            #     print('find number',part, delparts)

            # if re.match(r'\bV\d{2}\b', part):                         # V и две цифры могут означать порядковый номер
            #     newparts[1] = 'VS'
            #     delparts.append(part)
            #     print('find number', part, delparts)

            if re.match(r'\bWSH\b', part):                              # вариант обозначения военного щоденника
                newparts[1] = 'VS'
                delparts.append(part)
                continue

            if re.match(r'\d\d\d\d\d\d', part):                         # поиск возможной даты
                print('part = ',
                      part if datetime.strptime(part, "%d%m%y") < datetime.strptime(datefile, "%d%m%y") else datefile)
                if newparts[2] == 'DATE':
                    if datetime.strptime(part, "%d%m%y") < datetime.strptime(datefile, "%d%m%y"):
                        newparts[2] = part
                    else:
                        newparts[2] = datefile
                delparts.append(part)
                continue

            if len(part) == 3 and part in legaltypes:                   # поиск возможного типа
                if newparts[3] == 'TYPE':
                    newparts[3] = part
                delparts.append(part)
                continue

        if newparts[2] == 'DATE':                                       # дата в имени не найдена берем из свойств файла
            newparts[2] = datefile

        if newparts[3] == 'TYPE':                                     # стандартный тип в имени не найден, ищем варианты
            if re.search(r'\bVMZ', nametemp):
                newparts[3] = 'VMZ'
            if re.search(r'\bOTRAG', nametemp):
                newparts[3] = 'VMZ'
            if re.search(r'\bOTRAZHONKA', nametemp):
                newparts[3] = 'VMZ'
            if re.search(r'\bDAIDJEST', nametemp):
                newparts[3] = 'SUJ'
            if re.search(r'\bDAIDZHEST', nametemp):
                newparts[3] = 'SUJ'
            if re.search(r'\bDIDGEST', nametemp):
                newparts[3] = 'SUJ'
            if re.search(r'\bCYTATA', nametemp):
                newparts[3] = 'SNH'

        if newparts[3] == 'TYPE':                                       # тип не найден
            newparts.remove('TYPE')

        if newparts[1] == 'PROJECT':                                    # код проекта не установлен
            newparts.remove('PROJECT')
            # newparts[1] = 'UR'

        print(f'delparts : {delparts}')
        print(f'nameparts: {nameparts}')

        for part in delparts:                                           # удаляем из списка частей обработанные
            nameparts.remove(part)

        newparts += nameparts                                           # к шаблонной части добавляем специфическую
        newname = ''

        for x in range(len(newparts)):                                  # собираем новое имя
            if x == len(newparts) - 1:
                newname += newparts[x] + '.'
            else:
                newname += newparts[x] + ' '
        newname += exttemp                                              # возвращаем расширение файла
        print(f"NEW NAME: {newname}\n")
        os.rename(pathfile, join(split(pathfile)[0], newname))          # переименовываем
