from templates.SourceCodeFinderInterface import SourceCodeFinderInterface
from rich.console import Console


class GitHead(SourceCodeFinderInterface):
    def __init__(self, url):
        super().__init__(url)

    def find(self):
        console = Console()
        url = f'{self.url}/.git/logs/HEAD'
        try:
            request = self.send_get_request(url)
            response_blacklists = ['<html>', '<!DOCTYPE html>', '<body>', '</body>', '</html>']
            header = ["application/octet-stream"]
            http_status_codes = [200]
            header_match = request.headers.get('content-type') in header or request.headers.get('accept-ranges') == 'bytes'
            http_status_match = request.status_code in http_status_codes
            response_blacklist_match = request.text not in response_blacklists
            found = all([header_match, http_status_match, response_blacklist_match])
            if found:
                console.print(f'[bold green]Found: {url}')
                self.on_found(url)
            else:
                console.print(f'[bold yellow]Not Found: {url}')
        except Exception as e:
            console.print(f'[bold red]Error: {e}')

    def on_found(self, found):
        message = """
:rotating_light: *Git Head Found* :rotating_light:
:link: *URL*: {url}
:computer: 
`git-dumper {url} {domain}`

`GitTools/Dumper/gitdumper.sh {url}/.git/ {domain}-dump`

`GitTools/Extractor/extractor.sh {domain}-dump {domain}-extracted`

        """.format(url=self.url, domain=self.get_fqdn())
        self.save_result(found)
        self.notify_telegram(message)
