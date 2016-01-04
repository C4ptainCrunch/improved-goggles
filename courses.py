import requests
import requests_cache
from bs4 import BeautifulSoup
import base64

SESSION = open('session.cookie').read()
DOMAIN = base64.b64decode(b'YmV0YS5yZXNwdWJsaWNhZS5iZQ==').decode('ascii') # the domain name we are scraping

HEADERS = {
    'Host': DOMAIN,
    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/42.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

requests_cache.install_cache('requests', allowable_methods=['GET', 'POST', 'HEAD'])


def list_courses():
    cookies = {
        'ci_session': SESSION,
    }

    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://%s/subscriptions/courses' % DOMAIN,
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    headers.update(HEADERS)

    courses = []

    for i in range(0, 5000, 30):
        data = 'terms=&start=%i' % i
        resp = requests.post(
            'http://%s/ajax/get_courses' % DOMAIN,
            headers=headers, cookies=cookies, data=data
        )
        courses += resp.json()['data']

    courses_dict = {course['key_code']: course for course in courses}

    return courses_dict


def list_course_files(course_id):
    cookies = {
        'ci_session': SESSION,
    }

    resp = requests.get(
        'http://%s/documents/%s' % (DOMAIN, course_id),
        headers=HEADERS, cookies=cookies
    )
    resp.encoding = 'utf-8'

    soup = BeautifulSoup(resp.text, "html.parser")
    docs = soup.findAll("div", class_="big-list-item-infos")

    files = []

    for doc in docs:
        title = doc.find("p", class_="big-list-item-infos-title")
        page_url = title.a['href']
        files.append({
            'name': title.a.getText(),
            'pageurl': page_url
        })

    return files


def get_doc_url(page_url):
    cookies = {
        'ci_session': SESSION,
    }

    resp = requests.get(page_url, headers=HEADERS, cookies=cookies)
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.find("p", class_="download-button-wrapper").a['href']