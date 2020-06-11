from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time
from bs4 import BeautifulSoup
from collections import defaultdict
import re


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        urlCounter = {}
        words = defaultdict(int)
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            if (tbd_url not in urlCounter):
                urlCounter[tbd_url] = 1
            else:
                urlCounter[tbd_url] += 1
            try:
                if (urlCounter[tbd_url] < 10):
                    resp = download(tbd_url, self.config, self.logger)
                    self.logger.info(
                        f"Downloaded {tbd_url}, status <{resp.status}>, "
                        f"using cache {self.config.cache_server}.")
                    scraped_urls = scraper(tbd_url, resp)
                    for scraped_url in scraped_urls:
                        self.frontier.add_url(scraped_url)
                    self.frontier.mark_url_complete(tbd_url)

                   #WORD COUNTER

                    textContent = BeautifulSoup(resp.raw_response.content, features='lxml')

                    for line in textContent.find_all("p", text=True):
                        line = re.sub(r'[^\w]', ' ', line.get_text().lower())
                        for word in line.split():
                            words[word.encode('ascii', errors='ignore').decode()] += 1


                    time.sleep(self.config.time_delay)


            except Exception:
                    time.sleep(self.config.time_delay)
                    pass