from datetime import datetime as dt, timedelta
from collections import UserList
import pickle
from info import *
import os


class AddressBook(UserList):
    def __init__(self):
        self.data = []
        self.counter = -1

    def __str__(self):
        result = []
        for account in self.data:
            if account['birthday']:
                birth = account['birthday'].strftime("%d/%m/%Y")
            else:
                birth = ''
            if account['phones']:
                new_value = []
                for phone in account['phones']:
                    print(phone)
                    if phone:
                        new_value.append(phone)
                phone = ', '.join(new_value)
            else:
                phone = ''
            result.append(
                "_" * 50 + "\n" + f"Name: {account['name']} \nPhones: {phone} \nBirthday: {birth} \nEmail: {account['email']} \nStatus: {account['status']} \nNote: {account['note']}\n" + "_" * 50 + '\n')
        return '\n'.join(result)

    def __next__(self):
        phones = []
        self.counter += 1
        if self.data[self.counter]['birthday']:
            birth = self.data[self.counter]['birthday'].strftime("%d/%m/%Y")
        if self.counter == len(self.data):
            self.counter = -1
            raise StopIteration
        for number in self.data[self.counter]['phones']:
            if number:
                phones.append(number)
        result = "_" * 50 + "\n" + f"Name: {self.data[self.counter]['name']} \nPhones: {', '.join(phones)} \nBirthday: {birth} \nEmail: {self.data[self.counter]['email']} \nStatus: {self.data[self.counter]['status']} \nNote: {self.data[self.counter]['note']}\n" + "_" * 50
        return result

    def __iter__(self):
        return self

    def __setitem__(self, index, record):
        self.data[index] = {'name': record.name,
                            'phones': record.phones,
                            'birthday': record.birthday}

    def __getitem__(self, index):
        return self.data[index]

    def log(self, action):
        current_time = dt.strftime(dt.now(), '%H:%M:%S')
        message = f'[{current_time}] {action}'
        with open('logs.txt', 'a') as f:
            f.write(f'{message}\n')

    def add(self, record):
        newacc = {'name': record.name,
                   'phones': record.phones,
                   'birthday': record.birthday,
                   'email': record.email,
                   'status': record.status,
                   'note': record.note}
        self.data.append(newacc)
        self.log(f"Contact {record.name} has been added.")

    def save(self, file):
        # зберігає дані адресної книги у бінарний файл за вказаним ім'ям
        with open(file + '.bin', 'wb') as f:
            pickle.dump(self.data, f)
        self.log("Addressbook has been saved!")

    # завантажує дані адресної книги з бінарного файлу
    def load_pickle(self, file):
        try:
            with open(file + '.bin', 'wb') as f:
                self.data = pickle.load(f)
            self.log('Addressbook has been loaded')
        except FileNotFoundError:
            # виникає, якщо файл для адресної книги не знайдено
            self.log("Addressbook file not found. Creating a new one")
        except pickle.UnpicklingError:
            # виникає, якщо сталася помилка під час десеріалізації даних
            self.log("Error unplicking data. Creating a new address book")
        return self.data

    def load(self, file):
        return self.load_pickle(file)

    def search(self, pattern, category):
        result = []
        category_new = category.strip().lower().replace(' ', '')
        pattern_new = pattern.strip().lower().replace(' ', '')

        for account in self.data:
            if category_new == 'phones':

                for phone in account['phones']:

                    if phone.lower().startswith(pattern_new):
                        result.append(account)
            elif account[category_new].lower().replace(' ', '') == pattern_new:
                result.append(account)
        if not result:
            print('There is no such contact in address book!')
        return result

    def edit(self, contact_name, parameter, new_value):
        names = []
        try:
            for account in self.data:
                names.append(account['name'])
                if account['name'] == contact_name:
                    if parameter == 'birthday':
                        new_value = Birthday(new_value).value
                    elif parameter == 'email':
                        new_value = Email(new_value).value
                    elif parameter == 'status':
                        new_value = Status(new_value).value
                    elif parameter == 'phones':
                        new_contact = new_value.split(' ')
                        new_value = []
                        for number in new_contact:
                             new_value.append(Phone(number).value)
                    if parameter in account.keys():
                        account[parameter] = new_value
                    else:
                        raise ValueError
            if contact_name not in names:
                raise NameError
        except ValueError:
            print('Incorrect parameter! Please provide correct parameter')
        except NameError:
            print('There is no such contact in address book!')
        else:
            self.log(f"Contact {contact_name} has been edited!")
            return True
        return False

    def remove(self, pattern):
        flag = False
        for account in self.data:
            if account['name'] == pattern:
                self.data.remove(account)
                self.log(f"Contact {account['name']} has been removed!")
                flag = True
            '''if pattern in account['phones']:
                        account['phones'].remove(pattern)
                        self.log.log(f"Phone number of {account['name']} has been removed!")'''
        return flag

    def __get_current_week(self):
        now = dt.now()
        current_weekday = now.weekday()
        if current_weekday < 5:
            week_start = now - timedelta(days=2 + current_weekday)
        else:
            week_start = now - timedelta(days=current_weekday - 5)
        return [week_start.date(), week_start.date() + timedelta(days=7)]

    def congratulate(self):
        result = []
        WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_year = dt.now().year
        congratulate = {'Monday': [], 'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': []}
        for account in self.data:
            if account['birthday']:
                new_birthday = account['birthday'].replace(year=current_year)
                birthday_weekday = new_birthday.weekday()
                if self.__get_current_week()[0] <= new_birthday.date() < self.__get_current_week()[1]:
                    if birthday_weekday < 5:
                        congratulate[WEEKDAYS[birthday_weekday]].append(account['name'])
                    else:
                        congratulate['Monday'].append(account['name'])
        for key, value in congratulate.items():
            if len(value):
                result.append(f"{key}: {' '.join(value)}")
        return '_' * 50 + '\n' + '\n'.join(result) + '\n' + '_' * 50