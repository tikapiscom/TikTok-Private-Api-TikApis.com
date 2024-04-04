
import ssl
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, ProxyError, ConnectionError, Timeout, RequestException
import traceback
from urllib.parse import urlparse, urljoin
import json


class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        super().init_poolmanager(*args, **kwargs)


class HTTPRequester:
    def __init__(self, API_URL, API_HEADERS, proxies=None, app=None):
        self.app = app
        self.proxies = proxies
        self.API_URL = API_URL
        self.API_HEADERS = API_HEADERS
        self.ctx = self._create_ssl_context()
        self.session = self._create_client()

    @staticmethod
    def _create_ssl_context() -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        ciphers = (
            'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:'
            'ECDHE+AES256:ECDHE+AES128:DHE+AES256:DHE+AES128:'
            'RSA+AESGCM:RSA+AES:!aNULL:!eNULL:!MD5:!DSS:!RC4'
        )
        ctx.set_ciphers(ciphers)
        return ctx

    def _create_client(self):
        session = requests.Session()
        ssl_adapter = SSLAdapter(self.ctx)
        session.mount('https://', ssl_adapter)

        if self.proxies:
            session.proxies.update({
                'http': f'http://{self.proxies}',
                'https': f'http://{self.proxies}',
            })
        return session

    def complete_url(self, partial_url, base_url="https://"):
        parsed_url = urlparse(partial_url)
        if not parsed_url.scheme:
            return urljoin(base_url, partial_url)
        else:
            return partial_url

    def payload_data(self, data):
        if not data:
            return ""
        elif isinstance(data, bytes):
            return data.hex()
        elif isinstance(data, str):
            try:
                parsed_data = json.loads(data)
                return json.dumps(parsed_data)
            except ValueError:
                return data
        else:
            try:
                return json.dumps(data)
            except ValueError:
                return data

    def argus_redirect(self, url, data, headers):
        try:
            payload = json.dumps({
                **self.app,
                "url": url,
                "data": self.payload_data(data),
                "headers": json.dumps(headers)
            })
            response = requests.post(
                f"{self.API_URL}/sign/create", headers=self.API_HEADERS, data=payload)
            return response.json()
        except Exception as e:
            traceback.print_exc()

    def _send_request(self, method, url, headers=None, data=None, allow_redirects=False, **kwargs):
        try:
            history = []
            response = self.session.request(
                method, url, headers=headers, data=data, allow_redirects=allow_redirects, **kwargs)
            history.extend(response.history)
            while response.is_redirect:
                url = self.complete_url(response.headers['Location'])
                print("Redirecting to:", url)
                history.append(url)
                updated_headers = headers.copy() if headers else {}
                generated_headers = self.argus_redirect(
                    url, data if method == 'POST' and data else "", updated_headers)
                generated_headers.pop('Content-Type', None)
                updated_headers.update(generated_headers)
                if method == 'POST' and data:
                    response = self.session.request(
                        method, url, headers=updated_headers, data=data, allow_redirects=False, **kwargs)
                else:
                    response = self.session.request(
                        'GET', url, headers=updated_headers, allow_redirects=False, **kwargs)

            response.raise_for_status()
            return response
        except HTTPError as e:
            return {"error": "HTTP Error", "status_code": e.response.status_code, "reason": e.response.reason}
        except ProxyError as e:
            return {"error": "Proxy Error", "details": str(e)}
        except ConnectionError as e:
            return {"error": "Connection Error", "details": str(e)}
        except Timeout as e:
            return {"error": "Timeout Error", "details": str(e)}
        except RequestException as e:
            return {"error": "Request Exception", "details": str(e)}
        except Exception as e:
            return {"error": "General Error", "details": str(e), "traceback": traceback.format_exc()}

    def get(self, url, headers=None, **kwargs):
        return self._send_request('GET', url, headers=headers, **kwargs)

    def post(self, url, headers=None, data=None, **kwargs):
        return self._send_request('POST', url, headers=headers, data=data, **kwargs)
