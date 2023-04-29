from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger

import scraper
import time
import re
import tldextract
import numpy as np

from numpy.linalg import norm
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from difflib import SequenceMatcher
from urllib.parse import urlparse
from simhash import Simhash


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
        self.words = {}
        self.subdomains = {}
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
        subdomain_pattern = r'^(?:https?://)?([a-zA-Z0-9-]+\.)*(ics\.uci\.edu)(?:/|$)'
        match = re.match(subdomain_pattern, url)
        subdomain = match.group(1) if match else None

        if subdomain in self.subdomains:
            self.subdomains[subdomain] = self.subdomains[subdomain] + 1
        else:
            self.subdomains[subdomain] = 1

    def add_unique_page(self, url) -> None:
        """
        Adds an url to the set of unique pages.
        :param url: the url to add
        :return: void
        """
        self.unique_pages.add(url.split("#")[0])
        self.add_subdomain(url)

    def check_page(self, url) -> bool:
        """
        Checks if an url is already stored.
        :param url: the url to check.
        :return: True if it is already stored.
        """

        if url in self.unique_pages:
            return True
        else:
            return False

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
            if word in self.words:
                self.words[word] = self.words[word] + 1
            else:
                self.words[word] = 1

    def get_words(self):
        """
        Sorts the dict by most frequent word first, then returns it.
        :return: the sorted dictionary of words.
        """
        sorted_dict = sorted(self.words.items(), key=lambda x: x[1], reverse=True)

        file = open("output.txt", 'w')

        for entry in sorted_dict:
            file.write(entry[0] + " -> " + str(entry[1]))

        file.close()

    def get_subdomains(self):
        """
        Returns the list of subdomains.
        :return: the dictionary of subdomains.
        """

        file = open("subdomains.txt", 'w')

        sorted_dict = sorted(self.subdomains.items(), key=lambda x: x[1], reverse=True)

        for subdomain in sorted_dict:
            file.write(subdomain + " -> " + str(self.subdomains[subdomain]))

        file.close()


class TrapNavigator:
    def __init__(self):
        self.avoided_urls = []
        self.last_url = None
        self.token_hashes = {}
        self.url_hashes = {}

    def check_for_traps(self, url, tokens, results):
        """
        Run trap checks on the passed url.
        :param url: the url to check
        :param tokens: the tokens of the url to check
        :param results: the results object
        :return:
        """
        if self.known_traps(url, results):
            return True
        elif self.similarity_check(url, tokens):
            return True
        else:
            return False

    def similarity_check(self, new_url, tokens):
        """
        Checks for similarity between the current url and the new url.
        If the similarity score is too high, then return True.
        :param new_url: the url to check
        :param tokens: the tokens of the url to check
        :return: True if the score is very high, false otherwise.
        """

        url_simhash = Simhash(new_url).value
        token_simhash = Simhash(tokens).value

        if self.simhash_comparison_url(new_url, url_simhash):
            if self.simhash_comparison_tokens(new_url, token_simhash):
                return True

    def simhash_comparison_url(self, new_url, new_url_hash):
        """
        Compares the simhash comparison of a given URL with previously hashed URLs.
        :param new_url: the url to compare
        :param new_url_hash: the hashed url to compare
        :return: True if similarity threshold is passed.
        """

        for stored_hash in self.url_hashes.keys():
            if new_url_hash.distance(self.url_hashes[stored_hash]) < 3:
                return True

        self.add_hash_url(new_url, new_url_hash)
        return False

    def add_hash_url(self, new_url, new_url_hash):
        """
        Adds a hash of the new url to the dictionary of hashed urls.
        :param new_url: the url store
        :param new_url_hash: hash of the url
        :return:
        """

        self.url_hashes[new_url] = new_url_hash

    def simhash_comparison_tokens(self, new_url, token_hash):
        """
        Goes through the list of previously calculated sim hashes.
        If it detects a similar simhash, return True.
        :param new_url: url to compare to previously hashed websites.
        :param token_hash: the hash of tokens of the url to compare to previously hashed websites.
        :return: True if similar enough simhash found.
        """

        for url in self.token_hashes.keys():
            if self.hashes[url].distance(token_hash) < 3:
                return True

        self.add_hash_tokens(new_url, token_hash)
        return False

    def add_hash_tokens(self, new_url, token_hash):
        """
        Adds a url and its token hash.
        :param new_url: the url to add
        :param token_hash: a hash of a tokenized list of words.
        :return: void
        """

        self.token_hashes[new_url] = token_hash

    def known_traps(self, new_url, results: Results):
        """
        Checks for known traps.
        :param new_url: the url to check.
        :param results: the results object to update if a trap domain is located.
        :return:
        """

        if len(re.findall(r'/stayconnected/', new_url)) > 3:
            return True

        if len(re.findall(r'/computing/', new_url)) > 3:
            return True

        if "https://wiki.ics.uci.edu/doku.php" in new_url:
            results.add_subdomain(new_url)
            return True


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
        results = Results()
        trap_navigator = TrapNavigator()

        try:
            results.import_subdomain_json()
            results.import_word_json()
            results.import_longest_count()
            results.import_longest_page()
        except FileNotFoundError:
            print("Running for first time")

        results.export_log()

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
            tokens = tokenize(resp)

            # Add each token into the stored results.
            for token in tokens:
                results.add_word(token)

            # Update the current longest page length.
            results.update_longest_length(len(tokens))

            # For each obtained url, check for traps
            for scraped_url in scraped_urls:
                if results.check_page(scraped_url) or trap_navigator.check_for_traps(scraped_url, tokens):
                    pass
                else:
                    self.frontier.add_url(scraped_url)
                    trap_navigator.set_url(scraped_url)
                    trap_navigator.add_hash(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

            print(trap_navigator.url_hashes)

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

        results.print_words()
        results.export_longest_count()
        results.export_longest_page()
        results.print_subdomains()
