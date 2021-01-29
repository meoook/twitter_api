# Twitter API

* version: 0.01.2
* description: API to get **twitter user**, **user tweets** or **single tweet**
* author: [meok][author]
* depends: requests

### Inside package

- [x] Enterprise version - API 2.0
- [x] Guest version - API 1.1
- [x] Another guest version - API 1.1

# Example

```python
from twitter_api import TwitterApiV1, TwitterApiV2

# API 1.1 Example
twitter_api = TwitterApiV1()
tw_user = twitter_api.get_user(user_name='twitter_acc')
print(tw_user.data)

# API 2.0 Example (need develop acc beaver token)
token = 'twitter_enterprise_beaver_token'
twitter_api_v2 = TwitterApiV2(token)
tweets = twitter_api_v2.get_tweets(user_id='123456')
[print(tweet.data) for tweet in tweets]
```

# Release notes

| version | date     | changes                                                            |
| ------- | -------- | ------------------------------------------------------------------ |
| 0.01.02 | 28.01.21 | Remove not used package and session optimisation                   |
| 0.01.01 | 28.01.21 | Realise API v1.1 - Full done                                       |

[author]: <https://bazha.ru> "meok home page"
