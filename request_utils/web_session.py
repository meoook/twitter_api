import sys
import asyncio
import pyppeteer
import requests

from twitter_api.request_utils.random_agent import UserAgentGenerator

# Sanity checking.
try:
    assert sys.version_info.major == 3
    assert sys.version_info.minor > 5
except AssertionError:
    raise RuntimeError('Python 3.6+ required')


class WebSession(requests.Session):
    """ A browser session """
    def __init__(self, verify: bool = True):
        super().__init__()
        self.__browser = None
        self.__loop = None
        self.__verify: bool = verify

        _random_agents = UserAgentGenerator()
        self.headers['User-Agent'] = _random_agents.agent

    @property
    def browser(self):
        if not self.__browser:
            self.__loop = asyncio.get_event_loop()
            if self.__loop.is_running():
                raise RuntimeError("Cannot use browser in existing event __loop")
            self.__browser = self.__loop.run_until_complete(self.__get_browser())
        return self.__browser

    async def __get_browser(self):
        return await pyppeteer.launch(ignoreHTTPSErrors=not self.__verify, headless=True, args=['--no-sandbox'])

    def close(self):
        """ If a browser was created close it first """
        if self.__browser:
            self.__loop.run_until_complete(self.__browser.close())
        super().close()
