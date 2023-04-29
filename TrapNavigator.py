from urllib.parse import urlparse

class TrapNavigator:
    """
    Class to prevent traps.
    """

    def __init__(self):
        self.start_traps = [
            "wiki.ics.uci.edu/doku.php",
            "www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018",
            "www.ics.uci.edu/ugrad/current/policies/index.php",
            "www.ics.uci.edu/ugrad/policies",
            "www.ics.uci.edu/about/brenhall/index.php/",
            "www.ics.uci.edu/brenhall/brenhall",
            "www.ics.uci.edu/ugrad/policies/",
            "www.stat.uci.edu/damonbayer/uci_covid19_dashboard",
            "www.stat.uci.edu/damonbayer/uci_covid19_dashboard/blob/",
            "wics.ics.uci.edu/events/202",
            "archive.ics.uci.edu/ml/datasets/datasets/",
            "www.ics.uci.edu/honors/honors/",
            "www.ics.uci.edu/ugrad/honors/index.php"
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
        parsed = urlparse(new_url)
        noSchemeURL = parsed.netloc + parsed.path

        for s_trap in self.start_traps:
            if noSchemeURL.startswith(s_trap):
                return True

        for e_trap in self.end_traps:
            if noSchemeURL.endswith(e_trap):
                return True

        return False
