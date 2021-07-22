import requests
from .exceptions import PistonError


class PistonAPI:
    def __init__(self, endpoint="https://emkc.org/api/v2/piston"):
        self.endpoint = endpoint

    def _send(self, path, **payload):
        """Send a request to the server configured by self.endpoint

        Args:
            path (str): The path to be merged with the base url

        Returns:
            dict: The content of the response from the server
        """
        url = f"{self.endpoint}/{path}"
        response = requests.post(url, payload) if payload else requests.get(url)
        return PistonError.parse_response(response)

    @property
    def runtimes(self):
        return { item.pop("language"): item for item in self._send("runtimes") }

    @property
    def languages(self):
        return self.runtimes

    def execute(self, language, version, code, stdin="", args=[], timeout=10000):
        return self._send(
            "execute",
            language=language,
            version=version,
            files=[code],
            stdin=stdin,
            args=args,
            timeout=timeout,
        )["run"]["output"]