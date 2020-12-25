class CrawlerError(Exception):
    message: str
    link: str
    error: str


class CantOpenLinkError(CrawlerError):
    message = "can`t fetch link/exception"


class RobotsTxtError(CrawlerError):
    message = "parsing robots txt has error"


class RobotsTxtNotFoundError(CrawlerError):
    message = "robots.txt not found"


class RobotsTxtConnectionError(CrawlerError):
    message = "site haven`t robots.txt - ConnectionError"
