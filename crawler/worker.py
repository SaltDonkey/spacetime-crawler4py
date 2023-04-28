from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger

import scraper
import time
import re
import json

from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from urllib.parse import urldefrag
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
    """
    Class to prevent traps.
    """

    def __init__(self):
        self.start_traps = [
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
        self.end_traps = [
            "@uci.edu",
            "@ics.uci.edu",
            "@gmail.com",
            "void(0)"
        ]
        
    def check_for_traps(self, url):
        """
        Run trap checks on the passed url.
        :param url: the url to check
        :return:
        """
        if self.known_traps(url):
            return True
        else:
            return False

        # return self.similarity_check(url, tokens)

    def known_traps(self, new_url):
        """
        Checks for known traps.
        :param new_url: the url to check.
        :return:
        """

        for s_trap in self.start_traps:
            if new_url.startswith(s_trap):
                return True

        for e_trap in self.end_traps:
            if new_url.endswith(e_trap):
                return True

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

        infile.close()

    def export_longest_count(self):
        """
        Records the longest page count found.
        :return: None.
        """
        outfile = open("longest_count.txt", 'w')
        outfile.write(str(self.longest_page_count))

        outfile.close()

    def import_longest_count(self):
        """
        Loads the longest page count found.
        :return:
        """
        infile = open("longest_count.txt", 'r')
        self.longest_page_count = int(infile.readline())

        infile.close()

    def export_longest_page(self):
        """
        Records the longest page found
        :return: None.
        """
        outfile = open("longest.txt", 'w')
        outfile.write(self.longest_page)

        outfile.close()

    def import_longest_page(self):
        """
        Loads the longest file found
        :return:
        """
        infile = open("longest.txt", 'r')
        self.longest_page = infile.readline()

        infile.close()



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

        # Comment out if starting fresh crawl.
        results.import_subdomain_json()
        results.import_word_json()
        results.import_longest_count()
        results.import_longest_page()

        results.export_log()

        while True:

            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            if trap_navigator.known_traps(tbd_url):
                self.frontier.mark_url_complete(tbd_url)
                continue
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            if resp.status == 200:
                try:
                    real_url = resp.raw_response.url

                    scraped_urls = scraper.scraper(real_url, resp)

                    # Tokenize the response.
                    tokens = tokenize(resp)

                    # Add each token into the stored results.
                    for token in tokens:
                        results.add_word(token.lower())

                    # Update the current longest page length.
                    results.update_longest_length(len(tokens), real_url)

                    # For each obtained url, make sure it is not a trap.
                    for scraped_url in scraped_urls:
                        if not trap_navigator.known_traps(scraped_url):
                            self.frontier.add_url(scraped_url)
                            results.add_unique_page(scraped_url)
                    self.frontier.mark_url_complete(tbd_url)

                    # Debugging - Print word list length and current results.
                    # print(len(results.words))
                    # results.print_longest_length()

                    # Export relevant data - subdomains and word frequencies.
                    results.print_subdomains()
                    results.print_words()
                    results.export_longest_count()
                    results.export_longest_page()
                    results.export_subdomain_json()
                    results.export_word_json()

                except AttributeError:
                    self.frontier.mark_url_complete(tbd_url)
                    continue
            else:
                self.frontier.mark_url_complete(tbd_url)


            time.sleep(self.config.time_delay)

