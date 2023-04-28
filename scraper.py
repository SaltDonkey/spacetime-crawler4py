import re
import url_normalize
import math
import mmh3
from bs4 import BeautifulSoup
from collections import Counter
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin, urldefrag

class BloomFilter:
    def __init__(self, capacity, false_positive_rate):
        self.capacity = capacity
        self.false_positive_rate = false_positive_rate
        self.num_bits = int(-capacity * math.log(false_positive_rate) / (math.log(2)**2))
        self.num_hashes = int(self.num_bits * math.log(2) / capacity)
        self.bit_array = [False] * self.num_bits
        
    def add(self, item):
        for i in range(self.num_hashes):
            index = mmh3.hash(item, i) % self.num_bits
            self.bit_array[index] = True
            
    def __contains__(self, item):
        for i in range(self.num_hashes):
            index = mmh3.hash(item, i) % self.num_bits
            if not self.bit_array[index]:
                return False
        return True

EXCLUDE_PATTERN = re.compile(r".*.(css|js|bmp|gif|jpe?g|ico"
+ r"|png|tiff?|mid|mp2|mp3|mp4"
+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
+ r"|epub|dll|cnf|tgz|sha1"
+ r"|thmx|mso|arff|rtf|jar|csv"
+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$")

REGEX_PATTERN = re.compile(r".*\.(ics|cs|informatics|stat)\.uci\.edu$")
VISITED_URLS = BloomFilter(capacity=1000000, false_positive_rate=0.01)

#REGEX_PATTERN = re.compile(r".*\.(ics|cs|informatics|stat)\.uci\.edu(/.*|\.html|\.htm)$", re.IGNORECASE)

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def checkForRepeatingPath(parsedUrl):
    # Take our path and split them into a list to get each path argument
    # We do [1:] to omit the first "/"
    pathArgs = parsedUrl.path[1:].split("/")
    # Make a Counter of all separate path argument
    pathArgsCounter = Counter(pathArgs)

    # If any argument is repeated 3 or more times, we (most likely) have detected
    # a trap, exit and don't crawl
    for _, value in pathArgsCounter.most_common():
        if value >= 3:
            return True
    return False

# def removeFragmentAndQuery(url):
#     """
#     Removes the query and fragment section from the given url
#     """
#     # remove fragment section from the URL
#     url, _ = urldefrag(url)
    
#     # remove query section from the URL
#     url = urljoin(url, urlparse(url)._replace(query="").geturl())
    
#     return url


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
    links = set()
    # Check if response status code is 200 first, otherwise it will not be accessible
    if resp.status == 200:
        VISITED_URLS.add(url)
        # Parse the HTML content of the website using BeautifulSoup
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")

        # Extract the links from the webpage while being sure to defragment the URLs
        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                href = url_normalize.url_normalize(href)
                href = urldefrag(href)[0]
                # Check all the scraped links and check to see if they have a netloc/domain 
                parsed = urlparse(href)
                if not parsed.netloc and parsed.path:
                    href = urljoin(url, href)
                links.add(href)

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

        if checkForRepeatingPath(parsed):
            return False

        # This will make sure that URLs that download files are not 
        # considered to be valid
        if EXCLUDE_PATTERN.match(parsed.path.lower()):
            return False


        # The regex string will account for all URLs in this form:
        # *.ics.uci.edu/*
        # *.cs.uci.edu/*
        # *.informatics.uci.edu/*
        # *.stat.uci.edu/*
        # Overall match string is r".*\.(ics|cs|informatics|stat)\.uci\.edu$"
        return True if REGEX_PATTERN.match(parsed.netloc.lower()) else False


    except TypeError:
        print("TypeError for ", parsed)
        raise