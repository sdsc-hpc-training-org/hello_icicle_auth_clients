import logging
import sys
import typing


class ServerLogger:
    def initialize_logger(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler(stream=sys.stdout)

        file_handler = logging.FileHandler(
            r'logs.log', mode='w')
        stream_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

        # set formats
        stream_format = logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s')
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        stream_handler.setFormatter(stream_format)
        file_handler.setFormatter(file_format)

        # add the handlers
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

        self.logger.disabled = False


class ConnectionLogger:
    def initialize_logger(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_format = logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(stream_format)
        self.logger.addHandler(stream_handler)
        self.logger.disabled = False


class ServiceLogger:
    levels_map = {
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR
    }
    def __init__(self, name, log_path):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.file_handler = logging.FileHandler(
            log_path, mode='a')
        self.file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(file_format)
        self.logger.addHandler(self.file_handler)
        self.logger.disabled = False

    def log(self, data, level: typing.Literal['info', 'warning', 'error'], filename: str):
        self.file_handler.baseFilename = filename
        level = self.levels_map[level]
        self.logger.log(level, data)