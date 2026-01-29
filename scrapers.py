import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus


DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
}


def normalize_term(term):
    term = (term or '').strip().lower()
    return term.replace(' ', '-').replace('+', '-') if term else ''


def berlin_search(term):
    term = normalize_term(term)
    if not term:
        return []
    base = "https://berlinstartupjobs.com"
    url = f"{base}/skill-areas/{term}/"
    jobs = []
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    session.headers['Referer'] = base + '/'
    try:
        r = session.get(url, timeout=15)
        if r.status_code != 200:
            return []
        if r.encoding in (None, 'ISO-8859-1'):
            r.encoding = r.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        for el in soup.find_all('div', class_='bjs-jlid__wrapper'):
            job = {'source': 'berlinstartupjobs.com', 'company_name': '', 'job_title': '', 'description': '', 'job_link': ''}
            title_el = el.find('h4', class_='bjs-jlid__h')
            if title_el:
                a = title_el.find('a', href=True)
                if a:
                    job['job_title'] = a.get_text(strip=True)
                    href = a.get('href', '')
                    job['job_link'] = urljoin(base, href) if href and not href.startswith('http') else href
            company_el = el.find('a', class_='bjs-jlid__b')
            if company_el:
                job['company_name'] = company_el.get_text(strip=True)
            desc_el = el.find('div', class_=lambda c: c and ('description' in str(c).lower() or 'excerpt' in str(c).lower() or 'desc' in str(c).lower()))
            if desc_el:
                job['description'] = desc_el.get_text(strip=True)
            else:
                full = el.get_text(separator=' ', strip=True)
                for k in ('job_title', 'company_name'):
                    if job[k]:
                        full = full.replace(job[k], '', 1)
                job['description'] = ' '.join(full.split()[:50])
            if job['job_link']:
                jobs.append(job)
    except Exception:
        pass
    return jobs


def web3_search(term):
    term = normalize_term(term)
    if not term:
        return []
    base = "https://web3.career"
    url = f"{base}/{term}-jobs"
    jobs = []
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    try:
        r = session.get(url, timeout=15)
        if r.status_code != 200:
            return []
        if r.encoding in (None, 'ISO-8859-1'):
            r.encoding = r.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        for tr in soup.select('tr.table_row'):
            job = {'source': 'web3.career', 'company_name': '', 'job_title': '', 'description': '', 'job_link': ''}
            links = tr.find_all('a', href=True)
            job_links = [a for a in links if a.get('href') and '/jobs' not in a.get('href', '') and a.get('href', '').count('/') >= 2 and not a.get('href', '').startswith('http')]
            if not job_links:
                continue
            first = job_links[0]
            job['job_title'] = first.get_text(strip=True)
            href = first.get('href', '')
            job['job_link'] = urljoin(base, href) if href else ''
            if len(job_links) >= 2 and job_links[1].get('href') == href:
                job['company_name'] = job_links[1].get_text(strip=True)
            elif len(job_links) >= 2:
                job['company_name'] = job_links[1].get_text(strip=True)
            if not job['description']:
                job['description'] = job['job_title'] + ' at ' + (job['company_name'] or 'Company')
            if job['job_link']:
                jobs.append(job)
    except Exception:
        pass
    return jobs


def weworkremotely_search(term):
    term = (term or '').strip()
    if not term:
        return []
    base = "https://weworkremotely.com"
    q = quote_plus(term)
    url = f"{base}/remote-jobs/search?utf8=%E2%9C%93&term={q}"
    jobs = []
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    try:
        r = session.get(url, timeout=15)
        if r.status_code != 200:
            return []
        if 'Just a moment' in r.text or len(r.text) < 1000:
            return []
        if r.encoding in (None, 'ISO-8859-1'):
            r.encoding = r.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        job_links = soup.select('a[href*="/remote-jobs/"]')
        seen = set()
        for a in job_links:
            href = a.get('href', '')
            if not href or href in seen or href.count('/') < 3:
                continue
            if href.endswith('/remote-jobs') or '/remote-jobs/search' in href:
                continue
            seen.add(href)
            job = {'source': 'weworkremotely.com', 'company_name': '', 'job_title': '', 'description': '', 'job_link': ''}
            job['job_link'] = urljoin(base, href)
            job['job_title'] = a.get_text(strip=True) or 'Job'
            li = a.find_parent('li')
            if li:
                span = li.find('span', class_='company')
                if span:
                    job['company_name'] = span.get_text(strip=True)
                region = li.find('span', class_='region')
                if region:
                    job['description'] = region.get_text(strip=True)
            if not job['description']:
                job['description'] = job['job_title']
            jobs.append(job)
    except Exception:
        pass
    return jobs


def search_all(term):
    return {
        'berlinstartupjobs.com': berlin_search(term),
        'weworkremotely.com': weworkremotely_search(term),
        'web3.career': web3_search(term),
    }
