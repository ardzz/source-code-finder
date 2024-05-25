import concurrent.futures
import os
import time

from requests import get
from rich.console import Console

from templates.SourceCodeFinderInterface import SourceCodeFinderInterface


def get_files():
    return [
        "wwwroot", "htdocs", "www", "html", "web", "webapps", "public", "public_html"
        , "uploads", "website", "api", "test", "app", "backup", "backup_1", "backup_2"
        , "backup_3", "backup_4", "backups", "bin", "temp", "bak", "old", "db", "sql"
        , "dump", "database", "Release", "inetpub", "backend", "frontend", "config"
        , "production", "development", "prod", "dev", "stage", "staging", "live"
        , "test", "testing", "master"
    ]


def get_extensions():
    return [
        "tar", "7z", "bz2", "gz", "lz", "rar", "tar.gz", "tar.bz2", "xz", "zip", "z", "Z",
        "tar.z", "tar", "tgz", "db", "jar", "sqlite", "sqlitedb", "sql.7z", "sql.bz2", "sql.gz",
        "sql.lz", "sql.rar", "sql.tar.gz", "sql.xz", "sql.zip", "sql.z", "sql.tar.z"
    ]


def get_signature_binaries():
    strings = [
        "7573746172202000"  # tar
        , "7573746172003030"  # tar
        , "377ABCAF271C"  # 7z
        , "314159265359"  # bz2
        , "53514c69746520666f726d6174203300"  # SQLite format 3.
        , "1f8b"  # gz tar.gz
        , "526172211A0700"  # rar archive version 1.50
        , "526172211A070100"  # rar archive version 5.0
        , "FD377A585A0000"  # xz tar.xz
        , "1F9D"  # z tar.z
        , "1FA0"  # z tar.z
        , "4C5A4950"  # lz
        , "504B0304"  # zip
    ]

    # convert hex to binary
    binaries = []
    for string in strings:
        binaries.append(bytes.fromhex(string))
    return binaries


class ArchiveFileBackup(SourceCodeFinderInterface):
    def __init__(self, url):
        super().__init__(url)
        self.current_timeout_retry = 0

    def build_payload(self):
        domain = [
            self.get_domain_name(),
            self.get_fqdn(),
            self.get_subdomain(),
            self.get_rdn(),
        ]
        extension = get_extensions()
        files = get_files()

        payload = []
        for d in domain:
            if d is not None:
                for e in extension:
                    payload.append(f'{d}.{e}')

        for f in files:
            for e in extension:
                payload.append(f'{f}.{e}')

        return payload

    def find(self):
        files = get_files()
        extensions = get_extensions()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            x = 1
            for payload in self.build_payload():
                url = f"{self.url}/{payload}"
                executor.submit(self.send_request, url, x)
                x += 1

    def on_found(self, found):
        message = f"""
:rocket: *Archive File Backup Found* :rocket:
*URL*: {found[0][0]}
*Size*: {found[0][1]}
"""
        self.save_result(found[0][0])
        self.notify_telegram(message)

    def send_request(self, url, x):
        console = Console()
        # console.print(f"[{x}] Current timeout retry: {self.current_timeout_retry}")
        if self.current_timeout_retry >= self.max_timeout_retry:
            # console.print(f'[bold red][{x}] Max retries exceeded: {url}')
            return
        try:
            with get(url, stream=True, timeout=30, verify=False, allow_redirects=False) as response:
                max_bytes = 500  # bytes
                total_bytes = int(response.headers.get('content-length', 0))
                content = b''
                found = False
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=max_bytes):
                        content += chunk
                        if len(content) >= max_bytes:
                            break
                    for signature in get_signature_binaries():
                        if signature in content:
                            console.print(f'[bold green]Found: {url} [{total_bytes}]')
                            self.on_found([(url, total_bytes)])
                            found = True
                if not found:
                    console.print(f'[bold yellow]Not Found: {url}')
        except Exception as e:
            self.current_timeout_retry += 1
            console.print(f'[bold red]Error: {e}')
