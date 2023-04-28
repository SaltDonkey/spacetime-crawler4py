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
