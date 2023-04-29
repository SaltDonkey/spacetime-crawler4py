import re
import json

from collections import defaultdict
from urllib.parse import urlparse, urldefrag
from datetime import datetime

class Results:
    def __init__(self):
        """
        Class to store the assignment results.
        Stores:
            A set of unique pages
            The longest length of a page
            A dictionary of words
            A dictionary of subdomains
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
        self.unique_pages.add(urldefrag(url).url)
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
        else:
            pass

    def get_words(self) -> list:
        """
        Sorts the dict by most frequent word first, then returns it.
        :return: the sorted dictionary of words.
        """
        return self.words

    def get_subdomains(self) -> dict:
        """
        Returns the list of subdomains.
        :return: the dictionary of subdomains.
        """
        return self.subdomains

    def print_subdomains(self) -> None:
        """
        Writes the subdomains to file.
        """
        sorted_dict = sorted(self.subdomains.items(), key=lambda x: x[1], reverse=True)

        file = open("subdomainOutput.txt", 'w')

        for subdomain, count in sorted_dict:
            file.write(subdomain + " -> " + str(count) + "\n")

        file.close()

    def print_words(self) -> None:
        """
        Writes the words to file.
        """
        sorted_dict = sorted(self.words.items(), key=lambda x: x[1], reverse=True)

        file = open("words.txt", 'w')

        for word, count in sorted_dict:
            file.write(word + " -> " + str(count) + "\n")

        file.close()

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
        outfile = open("longest_page.txt", 'w')
        outfile.write(self.longest_page + "\n")

        outfile.close()

    def import_longest_page(self):
        """
        Loads the longest file found
        :return:
        """
        infile = open("longest_page.txt", 'r')
        self.longest_page = infile.readline()

        infile.close()