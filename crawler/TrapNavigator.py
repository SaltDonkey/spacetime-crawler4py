from simhash import Simhash

class TrapNavigator:
    def __init__(self):
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
        
        # If the new_url's simhash is similar to anything we have stored
        if self.simhash_comparison_url(new_url, url_simhash):
            # If the tokens of one page is similar to the tokens of the new url,
            # return True, they are similar
            if self.simhash_comparison_tokens(new_url, token_simhash):
                return True
        
        return False

    def simhash_comparison_url(self, new_url, new_url_hash):
        """
        Compares the simhash comparison of a given URL with previously hashed URLs.
        :param new_url: the url to compare
        :param new_url_hash: the hashed url to compare
        :return: True if similarity threshold is passed.
        """
        for stored_hash in self.url_hashes.keys():
            # If absolute value of the new_url_hash - url_hashes[stored_hash] is less than 3
            if abs(new_url_hash - self.url_hashes[stored_hash]) < 3:
                return True
        self.add_hash_url(new_url, new_url_hash)
        return False

    def simhash_comparison_tokens(self, new_url, token_hash):
        """
        Goes through the list of previously calculated sim hashes.
        If it detects a similar simhash, return True.
        :param new_url: url to compare to previously hashed websites.
        :param token_hash: the hash of tokens of the url to compare to previously hashed websites.
        :return: True if similar enough simhash found.
        """
        for url in self.token_hashes.keys():
            # If absolute value of the hashes[url] - token_hash is less than 3
            if abs(self.token_hashes[url] - token_hash) < 3:
                return True
        self.add_hash_tokens(new_url, token_hash)
        return False

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
            "https://archive.ics.uci.edu/ml/datasets/datasets/"
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