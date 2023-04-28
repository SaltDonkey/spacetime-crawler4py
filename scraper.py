import re
import url_normalize
from bs4 import BeautifulSoup
from collections import Counter
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin, urldefrag

REGEX_PATTERN = r".*\.(ics|cs|informatics|stat)\.uci\.edu$"
VISITED_URLS = set()


globalVisited = set()
urlRegex = re.compile(r".*\.(ics|cs|informatics|stat)\.uci\.edu(/.*|\.html|\.htm)$", re.IGNORECASE)

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

def removeFragmentAndQuery(url):
    """
    Removes the query and fragment section from the given url
    """
    return urljoin(url, urlparse(url).path)


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
<<<<<<< HEAD
    # Return a set with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    # Initialize set of links
    links = set()
 
    # Check if response status code is 200 and to see if the url is valid
    # If not, then an error occured or the url is invalid and we don't crawl,
    # return an empty list
    if resp.status != 200 or not is_valid(url):
        return links
    # Start the scraping here
    # Parse the HTML content of the website using BeautifulSoup
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    # Extract the links from the webpage
    # links.update([link.get("href") for link in soup.find_all("a")])
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            # Normalize the URL to avoid duplication
            href = url_normalize.url_normalize(href)
            links.add(href)
=======
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
        links = [removeFragmentAndQuery(link.get("href")) for link in soup.find_all("a")]

        # Check all the scraped links and check to see if they have a netloc/domain 
        # If they do not, then add the current URL's netloc/domain into the scraped link
        for i in range(len(links)):
            parsed = urlparse(links[i])
            if not parsed.netloc and parsed.path:
                links[i] = urljoin(url, links[i])
>>>>>>> master

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
        if url in globalVisited: #Returns false if already visited
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False

        if checkForRepeatingPath(parsed):
            return False

        # This will make sure that URLs that download files are not 
        # considered to be valid
        if re.match(
            r".*.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx)$", parsed.path.lower()):
            return False


        # The regex string will account for all URLs in this form:
        # *.ics.uci.edu/*
        # *.cs.uci.edu/*
        # *.informatics.uci.edu/*
        # *.stat.uci.edu/*
<<<<<<< HEAD
        # Overall match string is r".*(.ics.uci.edu/.*|.cs.uci.edu/.*|.informatics.uci.edu/.*|.stat.uci.edu/.*)$"
        if not urlRegex.match(url):
            return False
        
        globalVisited.add(url_normalize.url_normalize(url))

        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
urllist = ["https://www.ics.uci.edu/~kay/courses/i42/hw1.html",
        "https://www.cs.uci.edu/ugrad/degrees/degree_cs.php",
        "https://www.informatics.uci.edu/research/",
        "https://www.stat.uci.edu/undergraduate/minor-in-statistics/",
        "https://www.math.uci.edu/~chenlong/226/Ch2.pdf",
        "https://www.physics.uci.edu/~silverma/barn.html",
        "https://www.amazon.com/",
        "https://www.google.com/search?q=uci",
        "https://www.ics.uci.edu/",
        "https://www.ics.uci.edu/"]


if __name__ == '__main__':
    opt = input("Give opt\n")
    if opt == "man":
        yes = True
        while yes:
            url = input("Give url\n")
            if url == "stop":
                yes = False
            print(is_valid(url))
            for i in globalVisited:
                print(globalVisited)
    else:
        for u in urllist:
            print(u, "Is valid =", is_valid(u))
            print(len(globalVisited))

=======
        # Overall match string is r".*\.(ics|cs|informatics|stat)\.uci\.edu$"
        return re.match(REGEX_PATTERN, parsed.netloc.lower()) is not None

    except TypeError:
        print("TypeError for ", parsed)
        raise
>>>>>>> master
