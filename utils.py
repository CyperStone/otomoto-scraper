from time import sleep
from random import random


def go_to_sleep(a, b=None):
    if b is None:
        b = a
    sleep(a + random() * (b - a))


def parse_datetime(datetime_str):
    months_mapping = {
        'stycznia': 1,
        'lutego': 2,
        'marca': 3,
        'kwietnia': 4,
        'maja': 5,
        'czerwca': 6,
        'lipca': 7,
        'sierpnia': 8,
        'września': 9,
        'października': 10,
        'listopada': 11,
        'grudnia': 12
    }

    time, date = datetime_str.split(',')
    day, month, year = date.strip().split(' ')

    day = day.rjust(2, '0')
    month = str(months_mapping[month]).rjust(2, '0')

    return f'{year}-{month}-{day} {time}:00'


def format_time(seconds):
    seconds = round(seconds)
    total_seconds = seconds

    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    time_str = ''
    if days > 0:
        time_str += f'{days} day(s) '
    if hours > 0:
        time_str += f'{hours} hour(s) '
    if minutes > 0:
        time_str += f'{minutes} min(s) '
    if seconds > 0:
        time_str += f'{seconds} s '

    if total_seconds > 60:
        time_str += f'({total_seconds} s)'

    return time_str.strip()
