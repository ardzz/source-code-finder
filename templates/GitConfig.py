from templates.SourceCodeFinderInterface import SourceCodeFinderInterface
from rich.console import Console


class GitConfig(SourceCodeFinderInterface):
    def __init__(self, url):
        super().__init__(url)

    def find(self):
        console = Console()
        url = f'{self.url}/.git/config'
        try:
            request = self.send_get_request(url)
            # print(request.text.lower())
            response_blacklists = ['<html', '<body', '</script>']
            response_white_list = ['[core]', '[remote', '[url', '[branch', '[user', '[credentials]']
            http_status_codes = [200]
            match_response_blacklist = request.text.lower() not in response_blacklists
            match_http_status = request.status_code in http_status_codes
            match_white_list = any(word in request.text for word in response_white_list)
            found = all([match_response_blacklist, match_http_status, match_white_list])
            if found:
                console.print(f'[green]Found: {url}[/green]')
                self.on_found(url)
            else:
                console.print(f'[yellow]Not Found: {url}[/yellow]')
        except Exception as e:
            console.print(f'[red]Error: {e}[/red]')

    def on_found(self, found):
        message = """
:rotating_light: *Git Config Found* :rotating_light:
:link: *URL*: {url}
:warning: Config found but doesnt mean u can dump the repo
        """.format(url=found, domain=self.get_fqdn())

        self.save_result(found)
        self.notify_telegram(message)
