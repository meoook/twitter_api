import re
import time
import requests

from .tw_base import TwitterBase, logger
from .tw_types import TwUser, TwTweet

"""
    Use [TwitterApiV2] with enterprise token 
    Use [TwitterApiV1] for free access
    Use [TwitterApiV0] use if problems with V1
"""


class TwitterApiV1(TwitterBase):
    """ Twitter API 1.1 - guest access """
    def __init__(self):
        super().__init__()
        self.__token: str = self.__get_g_token()  # Guest token for API 1.1
        self.__x_guest: str = self.__get_x_token()  # X-Guest token for API 1.1

    def get_user(self, user_name: str = None, user_id: str = None) -> TwUser:
        """ Get twitter user profile using API 1.1 """
        assert user_name or user_id, 'User name or id must be set to get profile'
        _params = {'screen_name': user_name} if user_name else {'user_id': user_id}
        _params['include_entities'] = 'false'
        _url = self._URL_API + '1.1/users/show.json'
        _status, _data = self._request(url=_url, params=_params)
        if _status:
            return TwUser(_data)

    def get_tweets(self, user_id: str = None, amount: int = 10) -> list[TwTweet]:
        """ Get tweets for selected user using API 1.1 """
        _params = {'userId': user_id, 'count': self._fix_amount(amount)}
        _url = self._URL_WEB + f"i/api/2/timeline/profile/{user_id}.json"
        _status, _data = self._request(url=_url)
        if _status:
            _tweets_list: list = _data["globalObjects"]["tweets"]
            _tweets: list[TwTweet] = []
            for _tw_id in _tweets_list:
                _tw_data: dict = _tweets_list[_tw_id]
                if _tw_data['user_id_str'] == user_id:  # Filter not users tweets
                    _tweets.append(TwTweet(tw_data=_tw_data))
            return _tweets
        return []

    def get_tweet_info(self, tweet_id: str = None) -> TwTweet:
        """ Get single tweet info using API 1.1 """
        _url = self._URL_API + '1.1/statuses/show.json'
        _params = {'id': tweet_id, 'trim_user': 'true', 'include_entities': 'false'}
        _status, _data = self._request(url=_url, params=_params)
        if _status:
            return TwTweet(tw_data=_data)

    def __get_g_token(self) -> str:
        """ Get guest token using virtual browser """
        _session = requests.session()
        _session.headers.update({'User-Agent': self._agent})
        try:
            _response = _session.get(self._URL_WEB)
            _find_link = re.search(r'<link.*as=.script.*href=.(.*/main.*\.js)', _response.text)
            _script_link = _find_link.group(1)
            time.sleep(0.5)  # Twitter rate limit
            _response = _session.get(_script_link)
        except Exception as _err:
            logger.error(f'Get X-token err - {_err}')
        else:
            return re.search(r"A{20}.{84}", _response.text).group()

    def __get_x_token(self) -> str:
        """ X-Token for guest requests """
        _url = self._URL_API + "1.1/guest/activate.json"
        _header = {"Authorization": f"Bearer {self.__token}"}
        _response = requests.post(_url, headers=_header, proxies=self._proxy, verify=False)
        if _response.status_code not in [429, 403, 400]:
            _js_data = _response.json()
            if "guest_token" in _js_data:
                return _js_data["guest_token"]

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.__token}", "x-guest-token": self.__x_guest, "User-Agent": self._agent}


class TwitterApiV2(TwitterBase):
    # FIXME: Class not finished (check return) - cos no test
    #  tweet_type = tweet['referenced_tweets'][0]['type'] if 'referenced_tweets' in tweet else 'tweet'
    #  tweet_created = datetime.strptime(tweet['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
    """ Twitter API 2.0 - enterprise access """
    def __init__(self, enterprise_token):
        super().__init__()
        self.__token: str = enterprise_token  # Enterprise token for API 2.0

    def get_user(self, user_name: str = None, user_id: str = None) -> TwUser:
        """ Get twitter user profile using API 2.0 """
        assert user_name or user_id, 'User name or tweet_id must be set to get profile'
        _url_suffix = f'2/users/by/username/{user_name}' if user_name else f"2/users/{user_id}"
        _url = self._URL_API + _url_suffix
        _status, _data = self._request(url=_url)
        if _status:
            return TwUser(_data['data'])

    def get_tweets(self, user_id: str = None, amount: int = 10) -> list[TwTweet]:
        """ Get tweets for selected user using API 2.0 """
        _amount = self._fix_amount(amount)
        _url = self._URL_API + f"2/users/{user_id}/tweets"
        _params = {'max_results': _amount, 'tweet.fields': 'referenced_tweets,created_at'}
        _status, _data = self._request(url=_url, params=_params)
        if _status:
            _tweets_list: list = _data["globalObjects"]["tweets"]
            return [TwTweet(tw_data=_tweets_list[_tw_id]) for _tw_id in _tweets_list]
        return []

    def get_tweet_info(self, tweet_id: str = None) -> TwTweet:
        """ Get single tweet info using API 2.0 """
        _url = self._URL_API + f'/2/tweets/{tweet_id}'
        _status, _data = self._request(url=_url)
        if _status:
            return TwTweet(tw_data=_data)

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.__token}"}


class TwitterApiV0(TwitterApiV1):
    """ Twitter API 1.1 - guest access (old version) """
    def __init__(self):
        super().__init__()

    def get_user(self, user_name: str = None, user_id: str = None) -> TwUser:
        """ Get twitter user profile using API 1.1 (old) """
        assert user_name or user_id, 'User name or tweet_id must be set to get profile'
        _params = {'screen_name': user_name} if user_name else {'user_id': user_id}
        _url = self._URL_API + '1.1/users/lookup.json'
        _status, _data = self._request(url=_url, params=_params)
        if _status:
            if len(_data) == 0 or "errors" in _data:
                logger.error(f"User profile not found {user_name if bool(user_name) else user_id}")
            else:
                if len(_data) >= 2:
                    logger.warning(f'Too many results for profile response {_url}')
                return TwUser(_data[0])

    def get_tweet_info(self, tweet_id: str = None) -> TwTweet:
        """ Get single tweet info using API 1.1 (old) """
        _url = self._URL_WEB + f"i/api/2/timeline/conversation/{tweet_id}.json"
        _params = {'tweet_mode': 'extended', 'count': '1'}
        _status, _data = self._request(url=_url, params=_params)
        if _status:
            _tw_data = _data["globalObjects"]["tweets"][tweet_id]
            return TwTweet(tw_data=_tw_data)
