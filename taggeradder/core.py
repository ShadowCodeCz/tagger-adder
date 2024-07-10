import hashlib
import re
import json
import logging.config
import os
import glob
import apphelpers as app_helpers
import collections

import platform
import socket
import uuid
import datetime
import alphabetic_timestamp as ats

from dependency_injector import containers, providers
from . import notificator


class Container(containers.DeclarativeContainer):
    app_description = providers.Singleton(app_helpers.AppDescription, "tagger.adder")
    locale_paths = providers.Singleton(app_helpers.LocalePaths, app_description)
    package_paths = providers.Singleton(app_helpers.PackagePaths, app_description(), os.path.dirname(__file__))
    logger_helper = providers.Singleton(app_helpers.LoggerHelper, app_description, locale_paths)
    logger = providers.Factory(logging.getLogger, name=logger_helper().logger_name())
    help = providers.Singleton(app_helpers.Help, locale_paths, logger)
    locale_cfg_helper = providers.Singleton(app_helpers.Configuration, locale_paths, logger)
    cfg = providers.Configuration()
    notifier = providers.Singleton(notificator.SingletonNotificationProvider)


container = Container()


class MagTagger:
    def tags(self, params):
        dt = params.dt if params is not None else datetime.datetime.now()
        mag = ats.base62.from_datetime(dt, time_unit=ats.TimeUnit.seconds)
        return [f"mag@{mag}"]


class TimestampTagger:
    def tags(self, params):
        result = []
        dt = params.dt if params is not None else datetime.datetime.now()

        result.append(f"timestamp@{dt.timestamp()}")
        str_dt = dt.strftime("%Y.%m.%dT%H:%M:%S")
        str_year_month = dt.strftime("%Y.%m")
        str_month = dt.strftime("%B")
        result.append(f"datetime@{str_dt}")
        result.append(f"year.month@{str_year_month}")
        result.append(f"month@{str_month}")

        return result


class MachineTagger:
    def tags(self, params):
        result = []
        result.append(f"machine.platform.system@{self.remove_white_spaces(platform.system())}")
        result.append(f"machine.platform.release@{self.remove_white_spaces(platform.release())}")
        result.append(f"machine.platform.version@{self.remove_white_spaces(platform.version())}")
        result.append(f"machine.platform.architecture@{self.remove_white_spaces(platform.machine())}")
        result.append(f"machine.platform.processor@{self.remove_white_spaces(platform.processor())}")
        result.append(f"machine.socket.hostname@{self.remove_white_spaces(socket.gethostname())}")
        result.append(f"machine.socket.ip.address@{self.remove_white_spaces(socket.gethostbyname(socket.gethostname()))}")
        return result

    def remove_white_spaces(self, item):
        return str(item).replace(" ", "-")


class MacAddressTagger:
    def tags(self, params):
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        return [f"machine.socket.mac.address@{mac}"]