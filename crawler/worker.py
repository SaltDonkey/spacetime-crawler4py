from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger

import scraper
import time
import re
import tldextract
import json
import signal, sys

import numpy as np
from collections import defaultdict
from numpy.linalg import norm
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from difflib import SequenceMatcher
from urllib.parse import urlparse, urldefrag
from datetime import datetime

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


	
class TrapNavigator:
    def __init__(self):
        # self.avoided_urls = []
        # self.last_url = None
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
        if self.similarity_check(url, tokens):
            return True
        else:
            return False

        # return self.similarity_check(url, tokens)



    def known_traps(self, new_url, results):
        """
        Checks for known traps.
        :param new_url: the url to check.
        :param results: the results object to update if a trap domain is located.
        :return:
        """
        start_traps = [
            "https://wiki.ics.uci.edu/doku.php",
            "http://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018",
            "http://www.ics.uci.edu/ugrad/current/policies/index.php",
            "https://www.ics.uci.edu/ugrad/policies",
            "https://www.ics.uci.edu/about/brenhall/index.php/",
            "http://www.ics.uci.edu/brenhall/brenhall",
            "http://www.ics.uci.edu/ugrad/policies/",
            "https://www.stat.uci.edu/damonbayer/uci_covid19_dashboard",
            "https://www.stat.uci.edu/damonbayer/uci_covid19_dashboard/blob/",
            "https://wics.ics.uci.edu/events/202",
            "https://archive.ics.uci.edu/ml/datasets/datasets/",
            "http://www.ics.uci.edu/honors/honors/",
            "https://www.ics.uci.edu/ugrad/honors/index.php"
        ]

        end_traps = [
            "@uci.edu",
            "@ics.uci.edu",
            "@gmail.com",
        ]

        for s_trap in start_traps:
            if new_url.startswith(s_trap):
                return True

        for e_trap in end_traps:
            if new_url.endswith(e_trap):
                return True

        return False


    def add_hash_url(self, new_url, new_url_hash):
        """
        Adds a hash of the new url to the dictionary of hashed urls.
        :param new_url: the url store
        :param new_url_hash: hash of the url
        :return:
        """
        self.url_hashes[new_url] = new_url_hash

    def add_hash_tokens(self, new_url, token_hash):
        """
        Adds a url and its token hash.
        :param new_url: the url to add
        :param token_hash: a hash of a tokenized list of words.
        :return: void
        """
        self.token_hashes[new_url] = token_hash


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
        self.longest_page = ""
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
            if subdomain in self.subdomains:
                self.subdomains[subdomain] += 1
            else:
                self.subdomains[subdomain] = 1

    def add_unique_page(self, url) -> None:
        """
        Adds a url to the set of unique pages.
        :param url: the url to add
        :return: void
        """
        self.unique_pages.add(urldefrag(url).url) # can use urldefrag urldefrag(url).url instead of url.split("#")[0]
        self.add_subdomain(url)

    def update_longest_length(self, count, url) -> None:
        """
        Updates the current longest page length, if the
        passed length is greater.
        :param count: the count of the current page
        :return: void
        """
        if count > self.longest_page_count:
            self.longest_page_count = count
            self.longest_page = url

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
        else:
            pass

    def get_words(self) -> list:
        """
        Sorts the dict by most frequent word first, then returns it.
        :return: the sorted dictionary of words.
        """
        sorted_dict = sorted(self.words.items(), key=lambda x: x[1], reverse=True)

        for word, count in sorted_dict:
            print(word + " -> " + str(count))

        file = open("words.txt", 'w')

        for word, count in sorted_dict:
            file.write(word + " -> " + str(count))

        file.close()
        return sorted_dict

    def get_subdomains(self) -> dict:
        """
        Returns the list of subdomains.
        :return: the dictionary of subdomains.
        """
        # print(len(self.subdomains.keys()))
        # for subdomain in self.subdomains.keys():
        #     print(subdomain + " -> " + str(self.subdomains[subdomain]))
        sorted_dict = sorted(self.subdomains.items(), key=lambda x: (x[1], x[0]), reverse=True)

        file = open("subdomains.txt", 'w')

        for subdomain in sorted_dict:
            file.write(subdomain + " -> " + str(self.subdomains[subdomain]))

        file.close()

        return self.subdomains

    def print_subdomains(self) -> None:
        """
        Writes the subdomains to file.
        """
        sorted_dict = sorted(self.subdomains.items(), key=lambda x: x[1], reverse=True)

        file = open("subdomainOutput.txt", 'w')

        for line in sorted_dict:
            file.write(line[0] + " -> " + str(line[1]) + "\n")

    def print_words(self) -> None:
        """
        Writes the words to file.
        """
        # sorted_dict = sorted(self.words.items(), key=lambda x: x[1], reverse=True)
        #
        # file = open("subdomainOutput.txt", 'w')
        #
        # for line in sorted_dict:
        #     file.write(line)
        sorted_dict = sorted(self.words.items(), key=lambda x: x[1], reverse=True)

        file = open("words.txt", 'w')

        for line in sorted_dict:
            file.write(line[0] + " -> " + str(line[1]) + "\n")

        file.write("Longest page: " + self.longest_page + "\n")
        file.write("Longest length: " + str(self.longest_page_count))

    def export_word_json(self):
        """
        Exports the results.words dictionary to json.
        For stopping and continuing.
        :return: None
        """
        with open("wordJSON.json", "w") as outfile:
            json.dump(self.words, outfile)

        outfile.close()

    def import_word_json(self):
        """
        Imports the results.words dictionary from json.
        For stopping and continuing.
        :return: None
        """
        infile = open("wordJSON.json", "r")
        self.words = json.load(infile)

        infile.close()

    def export_subdomain_json(self):
        """
        Exports the subdomains to json.
        :return: None
        """
        with open("subdomainJSON.json", "w") as outfile:
            json.dump(self.subdomains, outfile)

        outfile.close()

    def import_subdomain_json(self):
        """
        Imports the subdomains from json.
        :return: None
        """
        infile = open("subdomainJSON.json", "r")
        self.subdomains = json.load(infile)

        infile.close()

    def export_log(self):
        """
        Updates the log file with crawl starts.
        :return:
        """
        infile = open("log.txt", 'a')
        infile.write(str(self.longest_page_count) + " " + str(datetime.now()) + "\n")

    def export_longest(self):
        """
        Records the longest page found and its length to a txt file.
        :return: None.
        """
        outfile = open("longest.txt", 'w')
        outfile.write(self.longest_page)
        outfile.write(str(self.longest_page_count))

    def import_longest(self):
        """
        Loads the longest file found and its length.
        :return:
        """
        infile = open("longest.txt", 'r')
        self.longest_page = infile.readline()
        self.longest_page_count = int(infile.readline())


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

        results.import_subdomain_json()
        results.import_word_json()
        results.import_longest()

        results.export_log()

        while True:

            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            if trap_navigator.known_traps(tbd_url, results):
                # print("Cancelling trap: " + tbd_url)
                self.frontier.mark_url_complete(tbd_url)
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

            # Add each token into the stored results.
            for token in tokens:
                results.add_word(token.lower())

            # Update the current longest page length.
            results.update_longest_length(len(tokens), tbd_url)

            # For each obtained url, check if each url was similar
            # than the last
            for scraped_url in scraped_urls:
                if not trap_navigator.known_traps(scraped_url, results):
                    self.frontier.add_url(scraped_url)
                    results.add_unique_page(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

            # Debugging - Print word list length and current results.
            # print(len(results.words))
            # results.print_longest_length()

            results.print_subdomains()
            results.print_words()
            results.export_longest()
            results.export_subdomain_json()
            results.export_word_json()

            time.sleep(self.config.time_delay)

