from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger
from Results import Results
from TrapNavigator import TrapNavigator
import scraper
import time
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from url_normalize import url_normalize

def tokenize(response):
    """
    Tokenize the passed html response.
    :param response: the web response.
    :return:
    """
    tokens = []
    if response.status == 200:
        try:
            soup = BeautifulSoup(response.raw_response.content, "lxml")
            tokenizer = RegexpTokenizer(r'\w+')
            tokens = tokenizer.tokenize(soup.get_text())
        except AttributeError:
            print("No content found.")

    return tokens


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {
            -1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {
            -1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

    def run(self):
        # Initialize our classes
        results = Results()
        trap_navigator = TrapNavigator()

        try:
            results.import_subdomain_json()
            results.import_word_json()
            results.import_longest()
        except FileNotFoundError:
            print("Running for first time")

        results.export_log()

        while True:
            tbd_url = self.frontier.get_tbd_url()
            
            # NORMALIZE URL
            tbd_url = url_normalize(str(tbd_url))
            # =============

            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            if trap_navigator.known_traps(tbd_url):
                print("Cancelling trap.")
                continue
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            scraped_urls = scraper.scraper(tbd_url, resp)

            # Tokenize the response.
            # print(tbd_url)
            tokens = tokenize(resp)
            # print(Simhash(tokens).value)
            # print(tbd_url)
            tokens = tokenize(resp)
            # print(Simhash(tokens).value)

            # Add each token into the stored results.
            for token in tokens:
                results.add_word(token.lower())
                results.add_word(token.lower())

            # Update the current longest page length.
            results.update_longest_length(len(tokens), tbd_url)
            results.update_longest_length(len(tokens), tbd_url)

            # For each obtained url, check if each url was similar
            # than the last
            for scraped_url in scraped_urls:
                if not trap_navigator.known_traps(scraped_url):
                    self.frontier.add_url(scraped_url)
                    results.add_unique_page(scraped_url)
                    results.add_unique_page(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

            # Debugging - Print word list length and current results.
            # print(len(results.words))
            # results.print_longest_length()

            results.print_subdomains()
            results.print_words()
            results.export_longest_count()
            results.export_longest_page()
            results.export_subdomain_json()
            results.export_word_json()

            time.sleep(self.config.time_delay)

        results.print_subdomains()
        results.print_words()
        results.export_longest_count()
        results.export_longest_page()
        results.export_subdomain_json()
        results.export_word_json()