import json
import os
import ctypes
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *

# import app_core
import qdarktheme
import datetime

from . import core
from . import gui
from . import notificator


class ApplicationCLI:
    @staticmethod
    def run(arguments):
        cfg = core.container.cfg
        cfg.from_json(arguments.configuration)
        app = Application(arguments.path, arguments.tags)
        app.run()


class Controller:
    def __init__(self):
        self.notifier = core.container.notifier()


class Application:
    def __init__(self, path, tags, logger=core.container.logger()):
        self.app = None
        self.logger = logger
        self.window = None
        self.arguments = None
        self.path = path
        self.tags = tags
        self.controller = Controller()

    def run(self):
        self.app = QApplication([])
        qdarktheme.setup_theme(corner_shape="sharp")
        self.window = gui.MainWindow()
        self.window.setWindowTitle(f"")
        self.set_logo()

        self.window.adder.tags_editor.load_tags(self.tags)
        self.window.show()
        self.app.exec()

    def set_logo(self):
        my_app_id = f'shadowcode.{core.container.app_description().name}.0.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        path = os.path.join(core.container.package_paths().image_directory(), 'logo.png')
        self.window.setWindowIcon(QIcon(path))
        self.app.setWindowIcon(QIcon(path))

    def __del__(self):
        text = self.window.adder.edit.edit.toPlainText().strip()

        if len(text) > 0:

            content = self.read_noter_file()
            content.append({
                "tags": self.window.adder.tags_editor.get_tags(),
                "text": text.split("\n")
            })
            self.write_note_file(content)

    def write_note_file(self, content):
        try:
            with open(self.path, "w+") as f:
                json.dump(content, f, indent=4)
        except Exception as e:
            self.logger.error(f"Fail during writing into {self.path} file")

    def read_noter_file(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Fail during reading {self.path} file")
                return []
        else:
            return []
