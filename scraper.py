import re
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin, urldefrag

REGEX_PATTERN = r".*\.(ics|cs|informatics|stat)\.uci\.edu$"
VISITED_URLS = set()

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

# def _robotParser(url):
#     # Create a RobotFileParser from urllib.parse
#     robotTxtParser = RobotFileParser()

#     # Set the robots.txt URL to parse by using urljoin()
#     robotTxtParser.set_url(urljoin(url, "/robots.txt"))

#     # Read and parse from the RobotFileParser
#     robotTxtParser.read()

#     # Return the object
#     return robotTxtParser

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
    
    # TODO: Can detect redirect by comparing url and resp.url?

    # Initialize list of links
    links = []

    # Check if response status code is 200 first, otherwise it will not be accesible
    if resp.status == 200:
        # Add the URL to the VISITED_SET of URLs
        VISITED_URLS.add(url)

        # Parse the HTML content of the website using BeautifulSoup
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")

        pageText = soup.get_text(strip = True, separator = " ")

        # Extract the links from the webpage while being sure to defragment the URLs
        links = [urldefrag(link.get("href")).url for link in soup.find_all("a")]

        # Check all the scraped links and check to see if they have a netloc/domain 
        # If they do not, then add the current URL's netloc/domain into the scraped link
        for i in range(len(links)):
            parsed = urlparse(links[i])
            if not parsed.netloc and parsed.path:
                links[i] = urljoin(url, links[i])

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
        # rp = _robotParser(url)

        # # Now check if current url is accessible based on robots.txt guidelines
        # # if not, then we cannot crawl, return False
        # if not rp.can_fetch("*", url):
        #     return False

        # Check if the url has been traversed already
        if url in VISITED_URLS:
            return False

        # Check if the url has http or https at the beginning
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # The regex string will account for all URLs in this form:
        # *.ics.uci.edu/*
        # *.cs.uci.edu/*
        # *.informatics.uci.edu/*
        # *.stat.uci.edu/*
        # Overall match string is r".*\.(ics|cs|informatics|stat)\.uci\.edu$"
        return re.match(REGEX_PATTERN, parsed.netloc.lower()) is not None

    except TypeError:
        print ("TypeError for ", parsed)
        raise