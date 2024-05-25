## Source Code Hunter
Source Code Hunter is a tool for searching for source code in an archive backup file & git miss-configured web servers. It is a tool that can be used to find source code in a web server that has been misconfigured and has a backup file or git directory exposed. This tool is useful for finding source code that has been accidentally exposed on a web server. It can be used to find sensitive information such as passwords, API keys, and other sensitive information that should not be exposed to the public. This tool is useful for penetration testers and security researchers who want to find source code that has been accidentally exposed on a web server. 

## Installation
To install Source Code Hunter, you can use the following commands:
```bash
git clone https://github.com/ardzz/source-code-finder.git
cd source-code-finder
pip install -r requirements.txt
```

## Usage
To use Source Code Hunter, you can use the following command:
```
usage: SourceCodeFinder.py [-h] [-u URL] [-f FILE]

Source Code Finder

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     Single URL to scan
  -f FILE, --file FILE  File containing URLs to scan
```

## Example
To use Source Code Hunter, you can use the following command:
```
python SourceCodeFinder.py -u http://example.com
```

## Configuration
Source Code Hunter can be configured by editing the `.env` file. You can change the following settings:
```env
TELEGRAM_CHAT_ID=
TELEGRAM_TOKEN=
THREAD_COUNT=1
TIMEOUT=30
```

The `TELEGRAM_CHAT_ID` and `TELEGRAM_TOKEN` settings are used to send notifications to a Telegram channel. You can create a Telegram bot and get the chat ID and token from the bot. The `THREAD_COUNT` setting is used to set the number of threads to use when scanning URLs. The `TIMEOUT` setting is used to set the timeout for each request.