import requests
import logging

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .tw_types import TwUser, TwTweet
from .random_agent import UserAgentGenerator

logger = logging.getLogger('twitter.api')


class TwitterBase:
    """ Twitter API base functions """
    _URL_WEB = "https://twitter.com/"
    _URL_API = "https://api.twitter.com/"
    __RATE_LIMIT_REMAINING_FOR_WARNING = 100  # Send warning when rate limit reach this limit
    __MINIMUM_TWEETS_PER_REQUEST = 5
    __MAXIMUM_TWEETS_PER_REQUEST = 100

    def __init__(self):
        """ Init user agent and disable warnings """
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable connection warnings
        self._agent: str = self.__user_agent_get_random()  # Set random user agent
        self.__proxy_enable: bool = False
        self.__proxy_http: str = ''
        self.__proxy_https: str = ''

    # Public function - implement for each class
    def get_user(self, user_name: str = None, user_id: str = None) -> TwUser: ...
    def get_tweets(self, user_id: str = None, amount: int = 20) -> list[TwTweet]: ...
    def get_tweet_info(self, tweet_id: str = None) -> TwTweet: ...

    def set_proxy(self, proxy_http: str, proxy_https: str) -> None:
        self.__proxy_enable = True
        self.__proxy_http: str = f"{proxy_http}"
        self.__proxy_https: str = f"{proxy_https}"
        logger.info(f'Proxy set http://{self.__proxy_http} https://{self.__proxy_https}')

    @property
    def _proxy(self) -> dict[str, str]:
        if self.__proxy_enable:
            return {"http": f"http://{self.__proxy_http}", "https": f"https://{self.__proxy_https}"}
        else:
            return {}

    def _request(self, url: str, params: dict = None) -> tuple[bool, any]:
        """ Request session with retry handle -> return json """
        try:
            logger.info(f'Request url {url} with params {params}')
            _response = requests.get(url, params=params, headers=self._headers, proxies=self._proxy, verify=False)
            self.__header_check_rate_limit(_response.headers)
        except requests.exceptions.SSLError:
            _err = f"proxy failed http://{self.__proxy_http} https://{self.__proxy_https}"
        except ConnectionError:
            _err = 'connection failed'
        else:
            _code = _response.status_code
            if _code < 300:
                return True, _response.json()
            elif _code == 429:
                # TODO: get more info about error
                #  _response.text = {"account_id":123123123,
                #  "product_name":"standard-basic",
                #  "title":"UsageCapExceeded",
                #  "period":"Monthly",
                #  "scope":"Product",
                #  "detail":"Usage cap exceeded: Monthly product cap",
                #  "type":"https://api.twitter.com/2/problems/usage-capped"}
                _err = f'request rate limit error'
            elif _code == 403:
                _err = f'request auth error'
            else:
                _err = f"request error code - {_code}"
        logger.error(_err)
        return False, _err

    @property
    def _headers(self) -> dict[str, str]:
        return {"User-Agent": self._agent}

    def __header_check_rate_limit(self, headers) -> None:
        """ Check Twitter API rate limit https://developer.twitter.com/en/docs/twitter-api/rate-limits """
        if 'x-rate-limit-remaining' in headers:
            remaining = headers['x-rate-limit-remaining']
            if int(remaining) < self.__RATE_LIMIT_REMAINING_FOR_WARNING:
                logger.warning(f'Rate limit reach warning level - remaining amount: {remaining}')
        else:
            logger.warning(f'No x-rate-limit-remaining in header')

    @staticmethod
    def __user_agent_get_random() -> str:
        _random_agents = UserAgentGenerator()
        return _random_agents.agent

    def _fix_amount(self, amount: int):
        if amount < self.__MINIMUM_TWEETS_PER_REQUEST:
            logger.warning(f'Twitter api minimum tweets per request is {self.__MINIMUM_TWEETS_PER_REQUEST}')
            return self.__MINIMUM_TWEETS_PER_REQUEST
        elif amount > self.__MAXIMUM_TWEETS_PER_REQUEST:
            logger.warning(f'Twitter api maximum tweets per request is {self.__MAXIMUM_TWEETS_PER_REQUEST}')
            return self.__MAXIMUM_TWEETS_PER_REQUEST
        else:
            return amount
