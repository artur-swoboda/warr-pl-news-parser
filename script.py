from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re, codecs, csv, htmlmin

with codecs.open('posts.csv', 'w', 'utf-8') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['ID', 'post_title', 'post_content', 'post_category', 'post_date', 'post_date_gmt'])

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print(e)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


"""
get links to pages
"""

# start_numba = 8
start_numba = 696
links = []
for x in range(start_numba, 0, -8):
    start = x
    end = start - 8

    raw_html = simple_get('http://www.warr.pl/2005/index.php?mode=news&pg_[go]={0}&pg_[go]={1}'.format(start, end))

    html = BeautifulSoup(raw_html, 'html.parser')

    temp_links = []
    for link in html.find_all('a'):
        if link.text == 'Zobacz więcej':
            temp_links.append(link.get('href'))

    links = links + list(reversed(temp_links))

"""
get page and parse it
"""

default_url = 'http://www.warr.pl/2005/'
page_1 = 'http://www.warr.pl/2005/index.php?mode=pnews&s=915'

print (len(links))

def parse_page(url):

	page_html = BeautifulSoup(simple_get(url), 'html.parser')

	"""
	page elements
	"""

	# get title and pub date
	page_title_block = page_html.select('td.td_tresc span.n_naglowek > b')
	page_title = cleanhtml(str(page_title_block[0]).split('<br/>')[0])
	page_data = cleanhtml(str(page_title_block[0]).split('<br/>')[1])

	# remove .naglowek
	for tag in page_html.select('span.n_naglowek'):
	    tag.decompose()

	for tag in page_html():
	    for attribute in ["style", ';', 'new', 'roman', 'times']:
	        del tag[attribute]

	page_content = page_html.select('td.td_tresc')[0]

	# print(page_title)
	# print(page_data)
	# print(page_content)

	return [page_title, page_content, page_data]

for x in range(len(links)):

	url = default_url + links[x]
	ID = 5000 + x
	data = parse_page(url)

	content = data[1]

	# content = htmlmin.minify(str(content), remove_empty_space=True)

	content = re.sub('<\/*td.*?>', '', str(content)) # remove TD
	content = re.sub('<\/*tr.*?>', '', str(content)) # remove TR
	content = re.sub('<\/*table.*?>', '', str(content)) # remove TABLE
	content = re.sub('<\/*tbody.*?>', '', str(content)) # remove TBODY
	content = re.sub('<\/*div.*?>', '', str(content)) # remove DIV
	content = re.sub('<\/*html.*?>', '', str(content)) # remove DIV
	content = re.sub('<\/*body.*?>', '', str(content)) # remove DIV

	content = content.rstrip()
	content = content.strip()

	with codecs.open('posts.csv', 'a', 'utf-8') as csvfile:
		post = csv.writer(csvfile, delimiter=',')
		post.writerow([ID, data[0], content, 'Aktualności', data[2], data[2]])
