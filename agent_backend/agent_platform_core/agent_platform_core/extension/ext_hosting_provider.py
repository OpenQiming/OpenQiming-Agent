from fastapi import FastAPI
from flask import Flask

from agent_platform_core.hosting_configuration import HostingConfiguration

hosting_configuration = HostingConfiguration()


def init_app(app: Flask):
    hosting_configuration.init_app(app)
