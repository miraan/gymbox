import requests
from lxml.html import fromstring, etree
from dateutil.parser import parse as parseDate
from datetime import datetime
from datetime import timedelta

session_requests = requests.Session()


def log(s):
    print datetime.now().strftime('%Y-%m-%d %H:%M:%S: ') + s


class GymboxClass:
    def __init__(self, id, class_name, time, instructor, duration):
        self.id = id
        self.class_name = class_name
        self.time = time
        self.instructor = instructor
        self.duration = duration

    def to_string(self):
        return self.time + ' ' + self.class_name + ' ' + self.instructor + ' ' + self.duration + ' ' + self.id

    def is_good_time(self):
        return int(self.time[:2]) >= 18


get_json_headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'gymbox.legendonlineservices.co.uk',
    'Pragma': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
get_page_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https//gymbox.legendonlineservices.co.uk',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
}
post_page_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https//gymbox.legendonlineservices.co.uk',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
}

book_url = 'https://gymbox.legendonlineservices.co.uk/enterprise/BookingsCentre/AddBooking'
pay_url = 'https://gymbox.legendonlineservices.co.uk/enterprise/Basket/Pay'
profile_url = 'https://gymbox.legendonlineservices.co.uk/enterprise/Account/PersonalProfile'
timetables = [
    {
        'club_name': 'Westfield London',
        'url': 'https://gymbox.legendonlineservices.co.uk/enterprise/BookingsCentre/MemberTimetable?clubId=6'
    },
    # {
    #     'club_name': 'Holborn',
    #     'url': 'https://gymbox.legendonlineservices.co.uk/enterprise/BookingsCentre/MemberTimetable?clubId=4'
    # },
    # {
    #     'club_name': 'Covent Garden',
    #     'url': 'https://gymbox.legendonlineservices.co.uk/enterprise/BookingsCentre/MemberTimetable?clubId=3'
    # }
]
classes_to_book = ['Hatha Yoga', 'Rocket Yoga', 'Vinyasa Flow Yoga', 'Ashtanga Yoga', 'Yin Yoga']


def book_classes():
    for timetable in timetables:
        log('Getting timetable for ' + timetable['club_name'])
        gymbox_classes = get_timetable(timetable['url'])
        print ''

        log('Got classes: ')
        for gymbox_class in gymbox_classes:
            log(gymbox_class.to_string())
        print ''

        to_book = list(filter(lambda x: x.class_name in classes_to_book and x.is_good_time(), gymbox_classes))
        for gymbox_class in to_book:
            book_class(gymbox_class)


def get_timetable(url):
    r = session_requests.get(url, headers=get_page_headers)
    doc = fromstring(r.text)
    # print etree.tostring(doc, pretty_print=True)

    table = doc.get_element_by_id('MemberTimetable')
    gymbox_classes = []
    tomorrow_classes = []
    tomorrow = datetime.now().date() + timedelta(days=1)
    current_day = None
    # print etree.tostring(table, pretty_print=True)

    for child in list(table):
        if child.get('class') == 'dayHeader':
            current_day_string = child.text_content()
            prefix = '&#160;&#160;'
            if current_day_string.startswith(prefix):
                current_day_string = current_day_string[len(prefix):]
            current_day = parseDate(current_day_string.encode('ascii', 'ignore').decode('ascii')).date()
        if current_day == tomorrow:
            tomorrow_classes.append(child)

    if len(tomorrow_classes) > 0:
        # Remove the dayHeader row and the column titles row
        del tomorrow_classes[0]
        del tomorrow_classes[0]

    for child in list(tomorrow_classes):
        time = child.find_class('col0Item')[0].text_content()
        class_name = child.find_class('col1Item')[0].text_content()
        instructor = child.find_class('col3Item')[0].text_content()
        duration = child.find_class('col4Item')[0].text_content()
        id = child.find_class('col5Item')[0][0].get('id')[5:]
        gymbox_classes.append(GymboxClass(id, class_name, time, instructor, duration))
    return gymbox_classes


def book_class(gymbox_class):
    log('Booking class ' + gymbox_class.to_string())

    url = book_url + '?booking=' + gymbox_class.id + '&ajax=0.05345021433000641'
    log('Request: ' + url)
    r = session_requests.get(url, headers=get_json_headers)
    log('Response: ' + r.text)
    print ''

    url = pay_url
    log('Request: ' + url)
    r = session_requests.get(url, headers=get_json_headers)
    log('Response Length: ' + len(r.text).__str__())
    print ''


def login():
    payload = {
        'login.Email': 'email@email.com',
        'login.Password': 'Password123'
    }
    r = session_requests.get('https://gymbox.legendonlineservices.co.uk/enterprise/account/login#',
                             headers=get_page_headers)
    r = session_requests.post('https://gymbox.legendonlineservices.co.uk/enterprise/account/login#', data=payload,
                              headers=post_page_headers)
    log('Logged In')


login()
book_classes()
book_classes() # Try again just in case there were errors
