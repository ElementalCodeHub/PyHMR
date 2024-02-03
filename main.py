import json
import subprocess
import time
import os
import logging.config
import click
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

@click.command()
@click.option('--config', default='hmr.config.json', help='Config file name.')
def start_hmr(config):
    # Define the default config file names
    default_config_filenames = ['default.config', 'hmr.config.json']

    # Initialize config_file_path to None
    config_file_path = None

    if config:
        # If custom config path is provided as an argument
        config_file_path = config
    else:
        # Get the current working directory
        current_dir = os.getcwd()

        # Check each default config filename in order
        for filename in default_config_filenames:
            default_config_path = os.path.join(current_dir, filename)
            if os.path.exists(default_config_path):
                config_file_path = default_config_path
                break

        # If none of the default config files are found, use hmr_config as the default config
        if not config_file_path:
            hmr_config = {
                "input": "src/main.py",
                "delay_ms": 5,
                "ignore": ["Scripts", ".src/__pycache__", "Lib", "Include"],
                "logging": {
                    "version": 1,
                    "handlers": {
                        "console": {
                            "class": "logging.StreamHandler",
                            "level": "INFO",
                            "formatter": "simple",
                            "stream": "ext://sys.stdout"
                        }
                    },
                    "formatters": {
                        "simple": {
                            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                        }
                    },
                    "root": {
                        "level": "INFO",
                        "handlers": ["console"]
                    }
                }
            }
            config_file_path = hmr_config

    defaultHMR = HMR(config_file_path)
    defaultHMR.start_watching()

class HMR():
    def __init__(self, config):
        if isinstance(config, dict):
            self.cfg = config
        else:
            with open(config) as config_file:
                self.cfg = json.load(config_file)

        self.input = self.cfg["input"]
        self.delay = int(self.cfg["delay_ms"]) / 1000
        self.ignore = self.cfg.get("ignore", [])
        self.setup_logging()
        self.event_handler = MyHandler(self)

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        logging_config = self.cfg.get("logging", {})
        logging.config.dictConfig(logging_config)

    def start_watching(self):
        observer = Observer()
        observer.schedule(self.event_handler, ".", recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def reload_script(self, msg=""):
        logging.info(msg)
        subprocess.Popen(["python", self.input])

class MyHandler(FileSystemEventHandler):
    def __init__(self, hmr_instance):
        self.hmr_instance = hmr_instance

    def on_modified(self, event):
        event_path = os.path.normpath(event.src_path)
        if event_path in self.hmr_instance.ignore:
            return  # Ignore specified directories or files
        else:
            logging.info(f'Reloading {event.src_path}')
            time.sleep(self.hmr_instance.delay)  # Wait for the specified delay before reloading
            self.hmr_instance.reload_script()

if __name__ == '__main__':
    start_hmr()
