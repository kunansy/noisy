import argparse
import asyncio
import datetime
import json
import logging
import random
import re
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from urllib3.exceptions import LocationParseError

REQUEST_TIMEOUT = 5


class CrawlerTimedOut(Exception):
    pass


class Crawler(object):
    def __init__(self):
        """
        Initializes the Crawl class
        """
        self._config = {}
        self._links = []
        self._start_time = None

    async def _request(self, url: str) -> Optional[str]:
        random_user_agent = random.choice(self._config["user_agents"])
        headers = {'user-agent': random_user_agent}
        timeout = aiohttp.ClientTimeout(REQUEST_TIMEOUT)

        async with aiohttp.ClientSession(timeout=timeout) as ses:
            logging.debug('%s: requesting', url)
            try:
                resp = await ses.get(url, headers=headers)
                resp.raise_for_status()
            except Exception:
                logging.error("%s: requesting error", url)
                return ''

        return await resp.text()

    @staticmethod
    def _normalize_link(link: str, root_url: str) -> Optional[str]:
        """
        Normalizes links extracted from the DOM by making them all absolute, so
        we can request them, for example, turns a "/images" link extracted from https://imgur.com
        to "https://imgur.com/images"
        :param link: link found in the DOM
        :param root_url: the URL the DOM was loaded from
        :return: absolute link
        """
        try:
            parsed_url = urlparse(link)
        except ValueError:
            # urlparse can get confused about urls with the ']'
            # character and thinks it must be a malformed IPv6 URL
            return None
        parsed_root_url = urlparse(root_url)

        # '//' means keep the current protocol used to access this URL
        if link.startswith("//"):
            return f"{parsed_root_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        # possibly a relative path
        if not parsed_url.scheme:
            return urljoin(root_url, link)

        return link

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        Check if a url is a valid url.
        Used to filter out invalid values that were found in the "href" attribute,
        for example "javascript:void(0)"
        taken from https://stackoverflow.com/questions/7160737
        :param url: url to be checked
        :return: boolean indicating whether the URL is valid or not
        """
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    def _is_blacklisted(self, url: str) -> bool:
        """
        Checks is a URL is blacklisted
        :param url: full URL
        :return: boolean indicating whether a URL is blacklisted or not
        """
        return any(
            blacklisted_url in url
            for blacklisted_url in self._config["blacklisted_urls"]
        )

    def _should_accept_url(self, url: str) -> bool:
        """
        filters url if it is blacklisted or not valid, we put filtering logic here
        :param url: full url to be checked
        :return: boolean of whether or not the url should be accepted and potentially visited
        """
        return url and self._is_valid_url(url) and not self._is_blacklisted(url)

    def _extract_urls(self, body: str, root_url: str) -> list[str]:
        """
        gathers links to be visited in the future from a web page's body.
        does it by finding "href" attributes in the DOM
        :param body: the HTML body to extract links from
        :param root_url: the root URL of the given body
        :return: list of extracted links
        """
        pattern = r"href=[\"'](?!#)(.*?)[\"'].*?"  # ignore links starting with #, no point in re-visiting the same page
        urls = re.findall(pattern, str(body))

        normalize_urls = [
            self._normalize_link(url, root_url)
            for url in urls
        ]

        return [
            url
            for url in normalize_urls
            if self._should_accept_url(url)
        ]

    def _remove_and_blacklist(self, link: str) -> None:
        """
        Removes a link from our current links list
        and blacklists it so we don't visit it in the future
        :param link: link to remove and blacklist
        """
        self._config['blacklisted_urls'] += [link]
        self._links.pop(self._links.index(link))

    async def _browse_from_links(self, depth: int = 0) -> None:
        """
        Selects a random link out of the available link list and visits it.
        Blacklists any link that is not responsive or that contains no other links.
        Please note that this function is recursive and will keep calling itself until
        a dead end has reached or when we ran out of links
        :param depth: our current link depth
        """
        is_depth_reached = depth >= self._config['max_depth']
        if not len(self._links) or is_depth_reached:
            logging.debug("Hit a dead end, moving to the next root URL")
            # escape from the recursion, we don't have links to continue or we have reached the max depth
            return

        if self._is_timeout_reached():
            raise CrawlerTimedOut

        random_link = random.choice(self._links)
        try:
            sub_page = await self._request(random_link)
            sub_links = self._extract_urls(sub_page, random_link)

            # sleep for a random amount of time
            time.sleep(random.randrange(self._config["min_sleep"], self._config["max_sleep"]))

            # make sure we have more than 1 link to pick from
            if len(sub_links) > 1:
                # extract links from the new page
                self._links = self._extract_urls(sub_page, random_link)
            else:
                # else retry with current link list
                # remove the dead-end link from our list
                self._remove_and_blacklist(random_link)

        except aiohttp.ClientError as e:
            logging.debug("%s: an exception occurred (%s), removing from list and trying again!",
                          random_link, repr(e))
            self._remove_and_blacklist(random_link)

        await self._browse_from_links(depth + 1)

    def load_config_file(self, file_path: Path) -> None:
        """
        Loads and decodes a JSON config file, sets the config of the crawler instance
        to the loaded one
        :param file_path: path of the config file
        :return:
        """
        with file_path.open() as config_file:
            config = json.load(config_file)
        self._config = config

    def set_option(self, option: str, value: Any) -> None:
        """
        Sets a specific key in the config dict
        :param option: the option key in the config, for example: "max_depth"
        :param value: value for the option
        """
        self._config[option] = value

    def _is_timeout_reached(self) -> bool:
        """
        Determines whether the specified timeout has reached, if no timeout
        is specified then return false
        :return: boolean indicating whether the timeout has reached
        """
        is_timed_out = False
        if timeout := self._config.get('timeout'):
            end_time = self._start_time + datetime.timedelta(seconds=timeout)
            is_timed_out = datetime.datetime.now() >= end_time

        return timeout and is_timed_out

    async def crawl(self) -> None:
        """
        Collects links from our root urls, stores them and then calls
        `_browse_from_links` to browse them
        """
        self._start_time = datetime.datetime.now()

        while True:
            url = random.choice(self._config["root_urls"])
            try:
                body = await self._request(url)
                self._links = self._extract_urls(body, url)
                logging.debug("found {} links".format(len(self._links)))
                await self._browse_from_links()

            except aiohttp.ClientError:
                logging.warning("%s: error connecting to root url", url)
                
            except MemoryError:
                logging.warning("%s: content is exhausting the memory",url)

            except LocationParseError:
                logging.warning("%s: error encountered during parsing", url)

            except CrawlerTimedOut:
                logging.info("Timeout has exceeded, exiting")
                return


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', metavar='-l', type=str, help='logging level', default='info')
    parser.add_argument('--config', metavar='-c', required=True, type=str, help='config file')
    parser.add_argument('--timeout', metavar='-t', required=False, type=int,
                        help='for how long the crawler should be running, in seconds', default=False)
    args = parser.parse_args()

    level = getattr(logging, args.log.upper())
    logging.basicConfig(level=level)

    crawler = Crawler()
    crawler.load_config_file(args.config)

    if args.timeout:
        crawler.set_option('timeout', args.timeout)

    await crawler.crawl()


if __name__ == '__main__':
    asyncio.run(main())
