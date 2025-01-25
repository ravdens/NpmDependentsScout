import colorama
from colorama import Fore, Style
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from typing import List, Optional
import configparser
import time
import pdb


# region Package Class
@dataclass
class Package:
    name: str
    url: str
    dependents: List[str]
    version: Optional[str] = None
    author: Optional[str] = None
    lastPublished: Optional[str] = None
    weeklyDownloads: Optional[int] = -1
    lastCheckedOn: str = ""  # Date when script checked

    def __eq__(self, other):
        if isinstance(other, Package):
            return self.name == other.name
        return False

@dataclass
class Author:
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    packageCount: int = 0
    lastCheckedOn: Optional[str] = None
    url: Optional[str] = None
    imageUrl: Optional[str] = None
    is_maintainer: bool = False
    monthlyDownloads: int = 0
    weeklyDownloads: int = 0
    depenents: int = 0

@dataclass
class Settings:
    npnStartPackage: str
    rabbitmqUrl: str
    cluster: bool
    npmBaseUrl: str
    activeTab: str
    npmUrl: str

# endregion

# region Config Functions
def get_settings():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    return Settings(
        npnStartPackage=config['settings']['npnStartPackage'],
        rabbitmqUrl=config['settings']['rabbitmqUrl'],
        cluster=config.getboolean('settings', 'cluster'),
        npmBaseUrl=config['settings']['npmBaseUrl'],
        activeTab=config['settings']['activeTab'],
        npmUrl=config['settings']['npmBaseUrl'] + "package/" + config['settings']['npnStartPackage'] + config['settings']['activeTab']
    )

# endregion

# region RabbitMQ


# endregion

# region CLI Display Functions

def cli_header():
    print(Fore.CYAN + "##################################################" + Style.RESET_ALL)
    print(Fore.CYAN + "##" + Style.RESET_ALL)
    print(Fore.CYAN + "##" + Style.RESET_ALL)

def cli_footer():
    print(Fore.CYAN + "##" + Style.RESET_ALL)
    print(Fore.CYAN + "##" + Style.RESET_ALL)
    print(Fore.CYAN + "##################################################" + Style.RESET_ALL)

def cli_title():
    print(Fore.CYAN + "##  NPM Package Scout" + Style.RESET_ALL)
    print(Fore.CYAN + "##" + Style.RESET_ALL)

def cli_webpage(url):
    print(Fore.CYAN + "##" + Style.RESET_ALL)
    print(Fore.CYAN + "##   " + Fore.WHITE + url + Style.RESET_ALL)
    print(Fore.CYAN + "##" + Style.RESET_ALL)

def cli_middle(input = None):
    if input:
        print(Fore.CYAN + "##" + Style.RESET_ALL)
        print(Fore.CYAN + "##   " + Fore.WHITE + input + Style.RESET_ALL)
        print(Fore.CYAN + "##" + Style.RESET_ALL)
    else:
        print(Fore.CYAN + "##" + Style.RESET_ALL)
        print(Fore.CYAN + "##" + Style.RESET_ALL)
        print(Fore.CYAN + "##" + Style.RESET_ALL)

# endregion

# region Soup Functions

def fetch_website_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(Fore.RED + f"Failed to fetch website: {url}." + Style.RESET_ALL)
        return None

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

def print_title(soup):
    title = soup.title.string
    print(Fore.GREEN + "Title of the webpage: " + Style.RESET_ALL + title)

def get_weekly_downloads(package_name):
    url = f"https://api.npmjs.org/downloads/point/last-week/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('downloads', 0)
    else:
        print(Fore.RED + f"Failed to fetch weekly downloads for {package_name}." + Style.RESET_ALL)
        return 0

@DeprecationWarning
def get_authors(soup):
    authors = []
    collaborators = soup.find(id="collaborators")
    if collaborators:
        ul_collaborators = collaborators.find_next('ul')
        if ul_collaborators:
            links = ul_collaborators.find_all('a')
            for link in links:
                print("++++")
                print(f"link: {link}")
                href = link.get('href')
                username = href.split('/~')[-1] if '/~' in href else ''
                img = link.find('img')
                image_url = img.get('src') if img else ''
                authors.append(Author(username=username, url=href, imageUrl=image_url, lastCheckedOn=str(int(time.time()))))
    return authors

def inspect_authors(authors):
    #TODO: scrape author details
    if authors is None:
        print(Fore.RED + "No authors found." + Style.RESET_ALL)
        return
    for author in authors:
        cli_middle(f"Author: {author.username}")
        cli_middle(f"URL: {author.url}")
        cli_middle(f"Image URL: {author.imageUrl}")
        cli_middle(f"Last Checked: {author.lastCheckedOn}")

#TODO: more logging incase something breaks?
def get_maintainers(package_name):
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        authors = []
        contributors = data.get('maintainers', [])
        for maintainer in contributors:
            authors.append(Author(username=maintainer.get('name'), email=maintainer.get('email'), lastCheckedOn=str(int(time.time())), is_maintainer=True))

        # Check if we've already noted the author before as a maintainer. Update to author and record name.
        versions = data["versions"]
        for version in versions:
            if "author" in versions[version]:
                if "email" in versions[version]["author"]:
                    for contributor in authors:
                        if contributor.email == versions[version]["author"]["email"]:
                            contributor.name = versions[version]["author"]["name"]
                            contributor.maintainer = False
                            break

        # Get more data for each contributor
        for contributor in authors:
            user_url = f"https://registry.npmjs.org/{contributor.username}"
            user_response = requests.get(user_url)
            if user_response.status_code == 200:
                user_data = user_response.json()
                first_key = next(iter(user_data))
                first_item = user_data[first_key]
                contributor.monthlyDownloads = first_item["downloads"]["monthly"]
                contributor.weeklyDownloads = first_item["downloads"]["weekly"]
                contributor.depenents = first_item["downloads"]["depenents"]

        return authors
    else:
        print(Fore.RED + f"Failed to fetch weekly downloads for {package_name}." + Style.RESET_ALL)
        return 0

def get_download_count(package_name):
    url = "https://api.npmjs.org/downloads/point/last-week/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('downloads', 0)
    else:
        print(Fore.RED + f"Failed to fetch download count for {package_name}." + Style.RESET_ALL)
        return 0

def get_dependents(soup):
    recorded_dependents = []
    dependents_list = soup.find(id="tabpanel-dependents")
    if dependents_list:
        ul_dependents = dependents_list.find_next('ul')
        if ul_dependents:
            deps = ul_dependents.find_all('a')

            # Check if there's more deps than listed on site
            if deps and deps[-1].get_text() == "and more...":
                dep_url = deps[-1].get('href')
                dep_html_content = fetch_website_content(settings.npmBaseUrl + dep_url)
                if dep_html_content:
                    more_soup = parse_html(dep_html_content)
                    more_dependents = get_more_dependents(more_soup)
                    return more_dependents

                #TODO: increase logging
                print(Fore.RED + f"Failed to fetch extended dependents for package." + Style.RESET_ALL)

            else:
                for dep in deps:
                    dep_link = dep.get('href').split('/')[-1]
                    dep_name = dep.get_text()
                    recorded_dependents.append(Package(name=dep_name, url=dep_link, dependents=[], lastCheckedOn=str(int(time.time()))))

    return recorded_dependents

def get_more_dependents(soup):
    recorded_dependents = []

    # Get all the dependents listed on the page
    dependents_list = soup.find(id="main")
    if dependents_list:
        ul_dependents = dependents_list.find_next('ul')
        if ul_dependents:
            deps = ul_dependents.find_all('a')
            for dep in deps:
                dep_link = dep.get('href').split('/')[-1]
                dep_name = dep.find('h3').get_text() if dep.find('h3') else None
                recorded_dependents.append(Package(name=dep_name, url=dep_link, dependents=[], lastCheckedOn=str(int(time.time()))))

    # Check if there's more dependents than listed on the page
    a_elements = soup.find_all(class_="a")
    for element in a_elements:
        if page.get_text() == "Next Page":
            next_page_url = page.get('href')
            next_page_html_content = fetch_website_content(settings.npmBaseUrl + next_page_url)
            if next_page_html_content:
                next_page_soup = parse_html(next_page_html_content)
                more_dependents = get_more_dependents(next_page_soup)
                recorded_dependents.extend(more_dependents)
                break
        
    if len(recorded_dependents) == 0:
        print(Fore.RED + f"No dependents found. Something went wrong." + Style.RESET_ALL)

    return recorded_dependents

def consolidate_packages(new_packages, known_packages):
    for new_package in new_packages:
        for known_package in known_packages:
            if new_package.name == known_package.name:
                new_package.dependents = known_package.dependents
                new_package.lastCheckedOn = known_package.lastCheckedOn
                break
    return new_packages

# endregion


def main():

    cli_header()
    cli_title()

    global settings
    settings = get_settings()

    cli_webpage(settings.npmUrl)

    html_content = fetch_website_content(settings.npmUrl)
    if html_content:
        soup = parse_html(html_content)
        #print_title(soup)

        contributors = get_maintainers(settings.npnStartPackage)
        inspect_authors(contributors)

        weekly_downloads = get_weekly_downloads(settings.npnStartPackage)
        if weekly_downloads:
            cli_middle(f"Weekly downloads: {weekly_downloads}")

        get_dependents(soup)

    else:
        print(Fore.RED + "Failed to retrieve the webpage." + Style.RESET_ALL)

    cli_footer()


if __name__ == "__main__":
    colorama.init()
    main()