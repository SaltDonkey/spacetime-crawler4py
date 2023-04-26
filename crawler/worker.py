from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger

import scraper
import time
import re
import tldextract

from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from difflib import SequenceMatcher
from urllib.parse import urlparse, urljoin, urldefrag


def _tokenize(response):
    """
    Tokenize the passed html response.
    :param response: the web response.
    :return:
    """
    tokens = []

    if response.status == 200:
        soup = BeautifulSoup(response.raw_response.content, "lxml")
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(soup.get_text())

    return tokens


class TrapNavigator:
    def __init__(self):
        self.avoided_urls = []
        self.last_url = None

    def check_for_traps(self, url):
        """
        Run trap checks on the passed url.
        :param url:
        :return:
        """
        if self.similarity_check(url):
            return True

    def set_url(self, new_url):
        """
        Sets the last_url
        :param new_url: the new url=
        :return: None
        """
        self.last_url = new_url

    def similarity_check(self, new_url):
        """
        Checks for similarity between the current url and the new url.
        If the similarity score is too high, then return True.
        :param new_url: the url to check
        :return: True if the score is very high, false otherwise.
        """
        # Maybe don't need? Just in case calling similarity_check for the first time
        if self.last_url is None:
            return False

        new_url_path = urlparse(new_url).path
        old_url_path = urlparse(self.last_url).path
        similarity_ratio = SequenceMatcher(None, new_url_path, old_url_path).ratio()

        if similarity_ratio > 0.97: # may need to lower?
            return True
        else:
            return False


class Results:
    def __init__(self):
        """
        Class to store the assignment results.
        Stores:
            A set of unique pages
            The longest length of a page
            A dictionary of words
            #TODO: A dictionary of subdomains
        """
        self.unique_pages = set()
        self.longest_page_count = 0
        self.words = defaultdict(int)
        self.subdomains = defaultdict(int)
        self.stopwords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
                          "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
                          "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
                          "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
                          "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
                          "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
                          "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
                          "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
                          "once", "only", "or", "other", "ought", "our", "ours	ourselves", "out", "over", "own",
                          "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
                          "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
                          "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
                          "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
                          "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
                          "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
                          "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
                          "yourself", "yourselves"]

    def add_subdomain(self, url) -> None:
        """
        # TODO - Not working yet.
        # TODO - Add checking to make sure the URL has a proper subdomain.
        Adds a subdomain to the subdomain results.
        If a given URL has a previously recorded subdomain, increments the
        subdomain's counter.
        :param url: the url with the subdomain of interest.
        :return: None
        """
        subdomain_pattern = r'^(?:https?://)?((?:[a-zA-Z0-9-]+\.)*ics\.uci\.edu)(?:/|$)'
        match = re.match(subdomain_pattern, url)
        subdomain = match.group(1) if match else None

        if subdomain:
            self.subdomains[subdomain] += 1

    def add_unique_page(self, url) -> None:
        """
        Adds a url to the set of unique pages.
        :param url: the url to add
        :return: void
        """
        self.unique_pages.add(urldefrag(url).url) # can use urldefrag urldefrag(url).url instead of url.split("#")[0]
        self.add_subdomain(url)

    def update_longest_length(self, count) -> None:
        """
        Updates the current longest page length, if the
        passed length is greater.
        :param count: the count of the current page
        :return: void
        """
        if count > self.longest_page_count:
            self.longest_page_count = count

    def print_longest_length(self) -> None:
        """
        Prints the current longest page length.
        For debugging.
        :return: void
        """
        print(self.longest_page_count)

    def add_word(self, new_word) -> None:
        """
        Adds the passed word to the word dict.
        If the word is already in the dict, increment its counter.
        :param new_word:
        :return:
        """
        word = new_word.lower()
        if word not in self.stopwords:
            self.words[word] += 1

    def get_words(self) -> list:
        """
        Sorts the dict by most frequent word first, then returns it.
        :return: the sorted dictionary of words.
        """
        sorted_dict = sorted(self.words.items(), key=lambda x: x[1], reverse=True)

        # for entry in sorted_dict:
        #     print(entry[0] + " -> " + str(entry[1]))

        for word, count in sorted_dict:
            print(word + " -> " + str(count))

        return sorted_dict

    def get_subdomains(self) -> dict:
        """
        Returns the list of subdomains.
        :return: the dictionary of subdomains.
        """
        print(len(self.subdomains.keys()))
        for subdomain in self.subdomains.keys():
            print(subdomain + " -> " + str(self.subdomains[subdomain]))

        return self.subdomains


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

        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            scraped_urls = scraper.scraper(tbd_url, resp)

            # Tokenize the response.
            tokens = _tokenize(resp)

            # Add each token into the stored results.
            for token in tokens:
                results.add_word(token)

            # Update the current longest page length.
            results.update_longest_length(len(tokens))

            # === TRAP DETECTION ===
            # TODO: Test/make it work 
            # TODO: See if we can make a hashmap/dictionary of checksums and their corresponding URLs
            # TODO: then for each scraped URL, reference that hashmap and see if the checksum/hash already
            # TODO: exists and then in that (similar) hashcode see if you can find a URL there?
            # Ex: website.com's tokens/text gives checksum 100
            # dict(100 : ["website.com"])
            # imposter.com tokens/text gives checksum 100 as well, 
            # since dict[100] exists, imposter.com is not added to our frontier 


            # For each obtained url, check if each url was similar
            # than the last
            for scraped_url in scraped_urls:
                if trap_navigator.check_for_traps(scraped_url):
                    pass
                else:
                    self.frontier.add_url(scraped_url)
                    trap_navigator.set_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

            # Debugging - Print word list length and current results.
            # print(len(results.words))
            # results.print_longest_length()
            # print(resp.url)

            time.sleep(self.config.time_delay)

        results.get_words()
        results.print_longest_length()
