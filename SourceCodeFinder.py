import os

from dotenv import load_dotenv
from rich.console import Console

from templates.PHPBackup import PHPBackup
from templates.ArchiveFileBackup import ArchiveFileBackup
from templates.GitConfig import GitConfig
from templates.GitHead import GitHead

import argparse

load_dotenv()
console = Console()

classes = [
    ArchiveFileBackup,
    PHPBackup,
    GitHead,
    GitConfig,
]

parser = argparse.ArgumentParser(description="Source Code Finder")
parser.add_argument("-u", "--url", type=str, help="Single URL to scan")
parser.add_argument("-f", "--file", type=str, help="File containing URLs to scan")
args = parser.parse_args()

targets = None

if args.url:
    targets = [args.url]
elif args.file:
    try:
        with open(args.file, "r") as f:
            targets = [line.strip() for line in f.read().strip().split("\n") if line.strip()]
    except FileNotFoundError:
        console.print("File not found!", style="bold red")
        exit(1)
else:
    parser.print_help()
    exit(1)

max_cpu_count = os.cpu_count() + 4
env_thread_count = int(os.getenv("THREAD_COUNT", 1))

if env_thread_count >= max_cpu_count:
    console.print(f"THREAD_COUNT is too high! THREAD_COUNT should be lower than {max_cpu_count}", style="bold red")
    exit(1)


for url in targets:
    for cls in classes:
        instance = cls(url.strip())
        console.print(f"Scanning {url.strip()} with {cls.__name__} Template", style="bold blue")
        instance.find()
        console.print(f"Scanning {url.strip()} with {cls.__name__} done!", style="bold green")
