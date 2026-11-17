"""Small, courteous HTTPS client. It stores no user text or credentials."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request


class SourceError(RuntimeError):
    def __init__(self, message: str, *, source: str = '', status: int | None = None):
        self.message = message
        self.source = source
        self.status = status
        super().__init__(message)


class HttpClient:
    def __init__(self, *, timeout: float = 30, interval: float = 1.1):
        self.timeout = timeout
        self.interval = interval
        self._last_request = 0.0

    def _request(self, url: str, payload=None) -> bytes:
        if not url.startswith('https://'):
            raise SourceError('Reference requests require HTTPS.', source=url)
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        headers = {'User-Agent': 'LetzTools/0.1 (Luxembourgish language references)',
                   'Accept': 'application/json,text/html,application/pdf;q=0.9,*/*;q=0.8'}
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        request = urllib.request.Request(url, data=body, headers=headers)
        try:
            self._last_request = time.monotonic()
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.read(20_000_001)
        except urllib.error.HTTPError as error:
            message = ('The official service is busy; try again later.' if error.code == 429
                       else f'The official service returned HTTP {error.code}.')
            raise SourceError(message, source=url, status=error.code) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise SourceError('The official service could not be reached. No check has been completed.', source=url) from None

    def get_bytes(self, url: str) -> bytes:
        data = self._request(url)
        if len(data) > 20_000_000:
            raise SourceError('The reference response exceeded the supported size.', source=url)
        return data

    def get_text(self, url: str) -> str:
        return self.get_bytes(url).decode('utf-8-sig', errors='replace')

    def get_json(self, url: str):
        try:
            return json.loads(self.get_text(url))
        except (ValueError, UnicodeError):
            raise SourceError('The official service returned an unexpected response.', source=url) from None

    def post_json(self, url: str, payload):
        try:
            return json.loads(self._request(url, payload).decode('utf-8-sig'))
        except (ValueError, UnicodeError):
            raise SourceError('The official service returned an unexpected response.', source=url) from None

# Both spellings are accepted by the small source adapters.
HTTPClient = HttpClient
