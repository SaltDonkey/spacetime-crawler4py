import re
from urllib.parse import urlparse

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = []
    
    if is_valid(url):
        pass
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # Namedtuple (scheme://netloc/path;parameters?query#fragment)
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # The regex string will account for all URLS in this form:
        # *.ics.uci.edu/*
        # *.cs.uci.edu/*
        # *.informatics.uci.edu/*
        # *.stat.uci.edu/*
        # Overall match string is r".*(.ics.uci.edu/.*|.cs.uci.edu/.*|.informatics.uci.edu/.*|.stat.uci.edu/.*)$"
        return not re.match(
            r".*(.ics.uci.edu/.*|" +
            r".cs.uci.edu/.*|" +
            r".informatics.uci.edu/.*|" +
            r".stat.uci.edu/.*)$", parsed.netloc.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise