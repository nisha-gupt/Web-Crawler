import re
from urllib.parse import urlparse, urldefrag
import urllib.robotparser
from lxml import html


robotDict = {}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    parsed = urlparse(url)
    robotURL = 'https://' + parsed.netloc + '/robots.txt'
    if (robotURL not in robotDict):
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robotURL)
        rp.read()
        robotDict[robotURL] = rp
    else:
        rp = robotDict[robotURL]
    links = set()
    if resp.status == 200 and rp.can_fetch('*', url):
        doc = html.fromstring(resp.raw_response.content)
        for l in doc.iterlinks():
            links.add(urldefrag(l[2])[0])
    return list(links)

def is_valid(url):
    if url:
        try:
            if url == "http://www.informatics.ics.uci.edu":
                return False
            parsed = urlparse(url)
            if parsed.scheme not in ["http", "https"]:
                return False
            if len(url) > 300:
                return False
            return not bool(re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())) and bool(re.match(r"\S*\.ics\.uci\.edu/\S*|\S*\.cs\.uci\.edu/\S*|\S*\.informatics\.uci\.edu/\S*|\S*\.stat\.uci\.edu/\S*|today\.uci\.edu/department/information_computer_sciences/\S*", ''.join(parsed).lower()))

        except TypeError:
            print ("TypeError for ", parsed)
            raise