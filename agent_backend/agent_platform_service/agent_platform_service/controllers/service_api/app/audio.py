import logging

from flask import request
from flask_restful import Resource, reqparse
from werkzeug.exceptions import InternalServerError

from agent_platform_service.controllers.service_api import api
from agent_platform_basic.exceptions.controllers.service_api.app import (
    AppUnavailableError,
    AudioTooLargeError,
    CompletionRequestError,
    NoAudioUploadedError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderNotSupportSpeechToTextError,
    ProviderQuotaExceededError,
    UnsupportedAudioTypeError,
)
from agent_platform_service.controllers.service_api.wraps import FetchUserArg, WhereisUserArg, validate_app_token
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_service.services.audio_service import AudioService
from agent_platform_basic.exceptions.services.audio import (
    AudioTooLargeServiceError,
    NoAudioUploadedServiceError,
    ProviderNotSupportSpeechToTextServiceError,
    UnsupportedAudioTypeServiceError,
)
from agent_platform_basic.exceptions.services.app_model_config import AppModelConfigBrokenError


class AudioApi(Resource):
    @validate_app_token(fetch_user_arg=FetchUserArg(fetch_from=WhereisUserArg.FORM))
    def post(self, app_model: App, end_user: EndUser):
        file = request.files['file']

        try:
            response = AudioService.transcript_asr(
                app_model=app_model,
                file=file,
                end_user=end_user
            )

            return response
        except AppModelConfigBrokenError:
            logging.exception("App model config broken.")
            raise AppUnavailableError()
        except NoAudioUploadedServiceError:
            raise NoAudioUploadedError()
        except AudioTooLargeServiceError as e:
            raise AudioTooLargeError(str(e))
        except UnsupportedAudioTypeServiceError:
            raise UnsupportedAudioTypeError()
        except ProviderNotSupportSpeechToTextServiceError:
            raise ProviderNotSupportSpeechToTextError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except ValueError as e:
            raise e
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


class TextApi(Resource):
    @validate_app_token(fetch_user_arg=FetchUserArg(fetch_from=WhereisUserArg.JSON))
    def post(self, app_model: App, end_user: EndUser):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True, nullable=False, location='json')
        parser.add_argument('voice', type=str, location='json')
        parser.add_argument('streaming', type=bool, required=False, nullable=False, location='json')
        args = parser.parse_args()

        try:
            response = AudioService.transcript_tts(
                app_model=app_model,
                text=args['text'],
                end_user=end_user,
                voice=args.get('voice'),
                streaming=args['streaming']
            )

            return response
        except AppModelConfigBrokenError:
            logging.exception("App model config broken.")
            raise AppUnavailableError()
        except NoAudioUploadedServiceError:
            raise NoAudioUploadedError()
        except AudioTooLargeServiceError as e:
            raise AudioTooLargeError(str(e))
        except UnsupportedAudioTypeServiceError:
            raise UnsupportedAudioTypeError()
        except ProviderNotSupportSpeechToTextServiceError:
            raise ProviderNotSupportSpeechToTextError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except ValueError as e:
            raise e
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


api.add_resource(AudioApi, '/audio-to-text')
api.add_resource(TextApi, '/text-to-audio')
