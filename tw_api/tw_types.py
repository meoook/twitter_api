from datetime import datetime


class TwUser:
    """ Data type to serialize user profile """
    def __init__(self, tw_data: dict):
        self.id = tw_data['id']
        self.name = tw_data['name']
        self.name_display = tw_data['screen_name'] if 'screen_name' in tw_data else tw_data.get('username')

    @property
    def data(self) -> dict[str, any]:
        return {'id': self.id, 'name': self.name, 'name_display': self.name_display}

    @property
    def url(self) -> str:
        return f'https://twitter.com/{self.name_display}'

    def __repr__(self):
        return f'<TwUser {self.name_display}>'


class TwTweet:
    """ Data type to serialize tweet """
    def __init__(self, tw_data: dict):
        _text = tw_data.get('full_text') or tw_data.get('text', '')
        self.id = tw_data['id_str']
        self.tw_type = self.__get_tw_type(tw_data)
        self.text = _text.strip().replace('\n', '')
        self.created_dt = datetime.strptime(tw_data['created_at'], "%a %b %d %H:%M:%S %z %Y")
        self.created = int(f'{self.created_dt.timestamp()}'.replace('.0', ''))
        self.lang = tw_data['lang']
        _likes = int(tw_data.get('favorite_count', 0))
        _relay = int(tw_data.get('reply_count', 0))
        _retweet = int(tw_data.get('retweet_count', 0))
        self.counts = {'like': _likes, 'relay': _relay, 'retweet': _retweet}

    @property
    def data(self) -> dict[str, any]:
        return {
            'id': self.id,
            'created': self.created,
            'lang': self.lang,
            'type': self.tw_type,
            'text': self.text,
            'counts': self.counts,
        }

    @staticmethod
    def __get_tw_type(tw_data: dict):
        """ Replay and comment - when done by self user """
        if tw_data.get('retweeted_status_id_str'):
            return 'retweet'
        elif tw_data.get('is_quote_status'):
            return 'reply' if tw_data.get('self_thread') else 'quote'
        else:
            return 'comment' if tw_data.get('self_thread') else 'tweet'

    def __repr__(self):
        return f'<TwTweet {self.id}>'
