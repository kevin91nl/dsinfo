import json
import os


class MetaFile:

    def __init__(self, path, logger=None):
        self.path = path
        self.logger = logger

    def read(self):
        if not os.path.exists(self.path):
            if self.logger:
                self.logger.debug('State file "{}" could not be found.'.format(self.path))
            return {}
        with open(self.path, 'r') as in_file:
            if self.logger:
                self.logger.debug('State file "{}" loaded...'.format(self.path))
            result = json.load(in_file)
        return result

    def write(self, data):
        with open(self.path, 'w') as out_file:
            if self.logger:
                self.logger.debug('Writing to state file "{}"...'.format(self.path))
            json.dump(data, out_file)
