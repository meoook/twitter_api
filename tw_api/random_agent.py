import random


class UserAgentGenerator:
    """ Get random user agent for http request """

    def __init__(self):
        self._pattern = r"Mozilla/5.0 ({}) AppleWebKit/603.3.8 (KHTML, like Gecko) Chrome/{} Mobile Safari/603.3.8"

    @property
    def agent(self) -> str:
        _os_v = self.__os_random
        _chrome_v = self.__chrome_v
        return self._pattern.format(_os_v, _chrome_v)

    @property
    def __chrome_v(self) -> str:
        _choices = range(43, 72)
        _version = random.choice(_choices)
        return f'87.0.42{_version}.0'

    @property
    def __os_random(self) -> str:
        _os_choices = [1, 2, 3, 4]
        _os = random.choice(_os_choices)
        if _os == 1:
            return self.__os_win()
        elif _os == 2:
            return self.__os_mac()
        elif _os == 3:
            return self.__os_android()
        else:
            return self.__os_iphone()

    @staticmethod
    def __os_win() -> str:
        _win_versions = ['10.0; Win64; x64', '10.0; WOW64', '6.1', '6.2', '6.3; Win64; x64']
        _version = random.choice(_win_versions)
        return f'Windows NT {_version}'

    @staticmethod
    def __os_mac() -> str:
        _os_x_versions = ['10_14_6', '10_15_6', '10_15_4', '10_13_6']
        _version = random.choice(_os_x_versions)
        return f'Macintosh; Intel Mac OS X {_version}'

    @staticmethod
    def __os_android() -> str:
        _android_device = ['Redmi 8', 'Nokia 8.1', 'SOV39', 'S68Pro', 'SXPro', 'M2003J15SC', 'ASUS_X00LDB', 'SM-G970U1'
                           'LM-V600', 'SAMSUNG-SM-J327A', 'U PULSE', 'KSA-LX9', 'GM1903', 'ASUS_X00TDB', 'H8266']
        _android_versions = ['10', '9', '8.1.1', '8.1.0', '8.0.0', '7.1.2', '7.1.1', '7.0', '6.0.1']
        _device = random.choice(_android_device)
        _version = random.choice(_android_versions)
        return f'Linux; Android {_version}; {_device}'

    @staticmethod
    def __os_iphone() -> str:
        _choices = ['CrOS x86_64 13482.0.0', 'CrOS x86_64 13483.0.0', 'Fedora; Linux x86_64', 'Linux x86_64']
        _version = random.choice(_choices)
        return f'X11; {_version}'
