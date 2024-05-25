import os
import concurrent.futures

from requests import get
from templates.SourceCodeFinderInterface import SourceCodeFinderInterface
from rich.console import Console

# disable insecure warnings
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

disable_warnings(InsecureRequestWarning)


class PHPBackup(SourceCodeFinderInterface):
    def __init__(self, url):
        super().__init__(url)
        self.current_timeout_retry = 0

    def get_paths(self):
        return [
            '/wp-config.php',  # WordPress
            '/wp-config',  # WordPress
            '/site/default/settings.php',  # drupal
            '/installation/configuration.php',  # joomla
            '/app/etc/env.php',  # magento
            '/Application/Common/Conf/config.php',  # thinkphp
            '/environments/dev/common/config/main-local.php',  # yii
            '/environments/prod/common/config/main-local.php',  # yii
            '/common/config/main-local.php',  # yii
            '/system/config/default.php',  # opencart
            '/typo3conf/localconf.php',  # typo3
            '/config/config_global.php',  # discuz
            '/config/config_ucenter.php',  # discuz
            '/textpattern/config.php',  # textpattern
            '/data/common.inc.php',  # dedecms
            '/caches/configs/database.php',  # phpcms
            '/caches/configs/system.php',  # phpcms
            '/include/config.inc.php',  # phpcms
            '/include/config.php',  # xbtit
            '/includes/config.php',  # vbulletin
            '/includes/config',  # vbulletin
            '/phpsso_server/caches/configs/database.php',  # phpcms
            '/phpsso_server/caches/configs/system.php',  # phpcms
            '/zb_users/c_option.php',  # zblog
            '/e/class/config.php',  # empirecms
            '/e/config/config.php',  # empirecms
            '/data/sql_config.php',  # phpwind
            '/data/bbscache/config.php',  # phpwind
            '/app/config/parameters.yml',  # prestashop 1.7
            '/app/config/parameters.php',  # prestashop 1.7
            '/config/settings.inc.php',  # prestashop  > 1.5,1.6
            '/config/settings.old.php',  # prestashop  > 1.5,1.6
            '/manager/includes/config.inc.php',  # MODX CMS
            '/app/config/parameters.ini',  # Symfony
            '/db.php',
            '/conn.php',
            '/database.php',
            '/db_config.php',
            '/config.inc.php',
            '/data/config.php',
            '/config/config.php',
            '/index.php',
            '/default.php',
            '/main.php',
            '/settings.php',
            '/header.php',
            '/footer.php',
            '/login.php',
            '/404.php',
            '/wp-login.php',
            '/config.php',
            '/config',
            '/const.DB.php.bak',
            '/const.DB.php'
        ]

    def get_extension(self):
        return [
            ".~", ".bk", ".bak", ".bkp", ".BAK", ".blank", ".swp",
            ".swo", ".swn", ".tmp", ".save", ".old", ".new", ".orig",
            ".dist", ".eski", ".txt", ".disabled", ".original", ".backup",
            "_bak", "_1.bak", "~", "!", ".0", ".1", ".2", ".3", ".4"
        ]

    def send_request(self, url):
        console = Console()
        if self.current_timeout_retry >= self.max_timeout_retry:
            return
        try:
            request = get(url, verify=False, timeout=30, allow_redirects=False)
            status_match = request.status_code == 200
            tag_match = any(word in request.text for word in ["<?php", "<?="]) and any(
                word in request.text for word in
                ["?>", "($", "$_GET[", "$_POST[", "$_REQUEST[", "$_SERVER[", "'DB_PASSWORD'",
                 "'DBPASS'", "database_type", "define('DB"])
            content_type_match = request.headers.get('content-type') == 'bytes' or request.headers.get(
                'content-type') == 'text/plain'
            if all([status_match, tag_match, content_type_match]):
                console.print(f'[bold green]Found: {url}')
                self.on_found(url)
            else:
                console.print(f'[bold yellow]Not Found: {url}')
        except Exception as e:
            self.current_timeout_retry += 1
            console.print(f'[bold red]Error: {url} - {e}')

    def find(self):
        console = Console()
        paths = self.get_paths()
        extensions = self.get_extension()
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            for path in paths:
                for extension in extensions:
                    url = f'{self.url}{path}{extension}'
                    executor.submit(self.send_request, url)

    def on_found(self, found):
        message = """
:rotating_light: *PHP Backup Found* :rotating_light:
:link: *URL*: {url}
:computer: `wget --no-check-certificate {url}`
        """.format(url=found)

        self.save_result(found)
        self.notify_telegram(message)
