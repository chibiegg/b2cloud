import ssl
import urllib3
from urllib3.util import ssl_
from requests.adapters import HTTPAdapter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HTTPSAdapter(HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = ssl_.create_urllib3_context(
            ciphers="AES256-SHA", cert_reqs=ssl.CERT_OPTIONAL, options=0
        )
        return super().init_poolmanager(*args, **kwargs)
