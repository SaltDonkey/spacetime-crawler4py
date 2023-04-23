import re
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
# import time

def scraper(url, resp):
    links = extract_next_links(url, resp)
    # time.sleep(0.5) # Pause for 0.5 seconds just to see if can be polite
    return [link for link in links if is_valid(link)]

def _robotParser(url):
    robotTxtParser = RobotFileParser()
    robotTxtParser.set_url(urljoin(url, "/robots.txt"))
    robotTxtParser.read()
    return robotTxtParser

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
    
    # Initialize list of links
    links = []

    # Check if response status code is 200 first, otherwise it will not be accesible
    if resp.status == 200:
        # Start the scraping here
        # Parse the HTML content of the website using BeautifulSoup
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")

        # Extract the links from the webpage
        links.extend([link.get("href") for link in soup.find_all("a")])
        
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # Namedtuple (scheme://netloc/path;parameters?query#fragment)

    # TODO: Check for looping/traps, check for webpage similarity (maybe don't have to), check to see if this thing works in the first place
    # TODO: Check for robots.txt (done?) and sitemaps
    try:
        # Create a RobotFileParser object and read from robots.txt for any allowed or disallowed content
        rp = _robotParser(url)

        # Now check if current url is accessible based on robots.txt guidelines
        # if not, then we cannot crawl, return False
        if not rp.can_fetch("*", url):
            return False

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