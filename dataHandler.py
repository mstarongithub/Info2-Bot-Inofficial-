"""
Saves the bot data to a local file.
"""

import json
from pathlib import Path

__authors__    = "Frederik Beimgraben"
__credits__    = ["Frederik Beimgraben"]
__maintainer__ = "Frederik Beimgraben"
__email__      = "beimgraben8@gmail.com"
__status__     = "WIP"

class BotData():
    def __init__(self, path='data.json', folder='db'):
        cwd = Path(__file__).parent.absolute()
        data_dir = cwd / 'data'
        if not data_dir.is_dir():
            data_dir.mkdir()
        db_dir = data_dir / 'db'
        if not db_dir.is_dir():
            db_dir.mkdir()
        if (db_dir / path).is_file():
            with open(path, 'r') as fp:
                self.data = json.load(fp)
        else:
            self.data = {'info': 'Bot-Data (surveys, user data, etc)'}
        self.path = db_dir / path
    
    def store(self):
        with open(self.path, 'r') as fp:
            self.data = json.dump(self.data, fp)