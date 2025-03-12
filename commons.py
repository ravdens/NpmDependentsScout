from typing import Optional, List
from dataclasses import dataclass

@dataclass
class Package:
    name: str
    url: str
    sourced_from: List[str]
    dependents: List[str]
    version: Optional[str] = None
    author: Optional[str] = None
    author_email: Optional[str] = None
    lastPublished: Optional[str] = None
    weeklyDownloads: Optional[int] = -1
    lastCheckedOn: str = ""  # Date when script checked

    @staticmethod
    def desearialize(data):
        """
        params: data: list[dict]
        returns: list[Package]
        """
        if type(data) != list:
            return []
        items_loaded = []
        for item in data:
            version = item.get('version', None)
            author = item.get('author', None)
            author_email = item.get('author_email', None)
            lastPublished = item.get('lastPublished', None)
            weeklyDownloads = item.get('weeklyDownloads', -1)

            items_loaded.append(Package(
                name=item.get("name"),
                url=item.get("url"),
                sourced_from=item.get("sourced_from"),
                dependents=item.get("dependents"),
                version=version,
                author=author,
                author_email=author_email,
                lastPublished=lastPublished,
                weeklyDownloads=weeklyDownloads,
                lastCheckedOn=item.get("lastCheckedOn")
            ))

        return items_loaded


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

    @staticmethod
    def desearialize(data):
        """
        params: data: list[dict]
        returns: list[Author]
        """
        if type(data) != list:
            return []
        items_loaded = []
        for item in data:
            name = item.get('name', None)
            username = item.get('username', None)
            email = item.get('email', None)
            lastCheckedOn = item.get('lastCheckedOn', None)
            url = item.get('url', None)
            imageUrl = item.get('imageUrl', None)

            items_loaded.append(
                Author(
                    name=name,
                    username=username,
                    email=email,
                    packageCount=item.get("packageCount"),
                    lastCheckedOn=lastCheckedOn,
                    url=url,
                    imageUrl=imageUrl,
                    is_maintainer=item.get("is_maintainer")
                )
            )
        return items_loaded

@dataclass
class Settings:
    npnStartPackage: str
    rabbitmqUrl: str
    cluster: bool
    npmBaseUrl: str
    activeTab: str
    npmUrl: str