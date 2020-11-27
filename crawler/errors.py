class CrawlerError(Exception):
    message: str


class RobotsTxtError(CrawlerError):
    pass


class RobotsTxtNotFoundError(CrawlerError):
