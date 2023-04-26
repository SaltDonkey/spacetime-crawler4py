import re
import url_normalize
from bs4 import BeautifulSoup
from urllib.parse import urlparse

globalVisited = set()
urlRegex = re.compile(r".*\.(ics|cs|informatics|stat)\.uci\.edu(/.*|\.html|\.htm)$", re.IGNORECASE)

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

        # TODO: Check for looping, check for webpage similarity, check to see if this thing works in the first place
        
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # Namedtuple (scheme://netloc/path;parameters?query#fragment)
    try:
        parsed = urlparse(url)
        if url in globalVisited: #Returns false if already visited
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False

        # The regex string will account for all URLS in this form:
        # *.ics.uci.edu/*
        # *.cs.uci.edu/*
        # *.informatics.uci.edu/*
        # *.stat.uci.edu/*
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

