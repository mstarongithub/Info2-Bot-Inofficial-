import json

class PistonError(Exception):
    @staticmethod
    def parse_response(response):
        content = json.loads(response.content)
        if len(content) == 1 and "message" in content:
            raise PistonError(content["message"])
        return content
