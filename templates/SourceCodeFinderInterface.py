import os
from datetime import datetime

import emojis
from requests import get

# disable insecure warnings
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

disable_warnings(InsecureRequestWarning)


class SourceCodeFinderInterface:
    def __init__(self, url):
        if not url.startswith('http') or not url.startswith('https'):
            url = f'https://{url}'
        if url.endswith('/'):
            url = url[:-1]
        self.url = url
        thread_count = max(1, int(os.getenv("THREAD_COUNT", 1)))
        self.thread_count = min(5, thread_count)
        self.max_timeout_retry = 3 if self.thread_count == 1 else thread_count
        self.timeout = int(os.getenv("TIMEOUT", 15))

    def find(self):
        pass

    def on_found(self, found):
        pass

    # fqdn = fully qualified domain name
    def get_fqdn(self):
        try:
            return self.url.split('//')[1]
        except:
            return None

    # rdn = relative domain name
    # www.google.com -> google.com
    def get_rdn(self):
        # if country code included
        try:
            if len(self.get_fqdn().split('.')) > 2:
                return '.'.join(self.get_fqdn().split('.')[1:])
            else:
                return self.get_fqdn()
        except:
            return None

    # get domain name www.google.com -> google
    def get_domain_name(self):
        try:
            return self.get_fqdn().split('.')[1]
        except:
            return None

    def get_subdomain(self):
        try:
            return self.get_fqdn().split('.')[0]
        except:
            return None

    def save_result(self, result):
        # get child class name
        class_name = self.__class__.__name__
        current_date = datetime.now().strftime('%Y-%m-%d')
        dir_path = f'results/'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(f'{dir_path}{class_name}_{current_date}.txt', 'a') as f:
            f.write(result + '\n')

    def notify_telegram(self, message):
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        token = os.getenv('TELEGRAM_TOKEN')
        message = emojis.encode(message)
        if chat_id and token:
            url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&parse_mode=markdown&text={message}'
            self.send_get_request(url)

    def send_get_request(self, url):
        try:
            request = get(url, verify=False, timeout=self.timeout, allow_redirects=False, headers={'User-Agent': self.random_ua()})
            return request
        except Exception as e:
            raise e

    def random_ua(self):
        # you can also import SoftwareEngine, HardwareType, SoftwareType, Popularity from random_user_agent.params
        # you can also set number of user agents required by providing `limit` as parameter

        software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.EDGE.value,
                          SoftwareName.EDGE.value, SoftwareName.OPERA.value, SoftwareName.SAFARI.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value,
                             OperatingSystem.ANDROID.value, OperatingSystem.IOS.value, OperatingSystem.CHROMEOS.value]

        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

        # Get Random User Agent String.
        return user_agent_rotator.get_random_user_agent()
