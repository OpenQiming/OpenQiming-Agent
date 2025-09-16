import json
import logging

import requests
from flask import current_app
from flask_restful import Resource, reqparse

from . import api


class VersionApi(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('current_version', type=str, required=True, location='args')

        result = {
            'version': current_app.config['CURRENT_VERSION'],
            'release_date': '',
            'release_notes': '',
            'can_auto_update': False,
            'features': {
                # 'can_replace_logo': current_app.config['CAN_REPLACE_LOGO'],
                'model_load_balancing_enabled': current_app.config['MODEL_LB_ENABLED']
            }
        }

        return result


api.add_resource(VersionApi, '/version')
