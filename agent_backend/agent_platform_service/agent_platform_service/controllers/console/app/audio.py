import logging

from flask import request
from flask_restful import Resource, reqparse
from werkzeug.exceptions import InternalServerError

from agent_platform_basic.exceptions.controllers.console.app import (
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
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.exceptions.services.app_model_config import AppModelConfigBrokenError
from agent_platform_basic.exceptions.services.audio import (
    AudioTooLargeServiceError,
    NoAudioUploadedServiceError,
    ProviderNotSupportSpeechToTextServiceError,
    UnsupportedAudioTypeServiceError,
)
from agent_platform_basic.exceptions.services.audio import ProviderNotSupportTextToSpeechLanageServiceError
from agent_platform_basic.libs.login import login_required
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.app.wraps import get_app_model
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.services.audio_service import AudioService


class ChatMessageAudioApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    def post(self, app_model):
        file = request.files['file']

        try:
            response = AudioService.transcript_asr(
                app_model=app_model,
                file=file,
                end_user=None,
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
            logging.exception(f"internal server error, {str(e)}.")
            raise InternalServerError()


class ChatMessageTextApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model
    def post(self, app_model):
        try:
            response = AudioService.transcript_tts(
                app_model=app_model,
                text=request.form['text'],
                voice=request.form['voice'],
                streaming=False
            )

            return {'data': response.data.decode('latin1')}
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
            logging.exception(f"internal server error, {str(e)}.")
            raise InternalServerError()


class TextModesApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model
    def get(self, app_model):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('language', type=str, required=True, location='args')
            args = parser.parse_args()

            response = AudioService.transcript_tts_voices(
                tenant_id=app_model.tenant_id,
                language=args['language'],
            )

            return response
        except ProviderNotSupportTextToSpeechLanageServiceError:
            raise AppUnavailableError("Text to audio voices language parameter loss.")
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
            logging.exception(f"internal server error, {str(e)}.")
            raise InternalServerError()


api.add_resource(ChatMessageAudioApi, '/apps/<uuid:app_id>/audio-to-text')
api.add_resource(ChatMessageTextApi, '/apps/<uuid:app_id>/text-to-audio')
api.add_resource(TextModesApi, '/apps/<uuid:app_id>/text-to-audio/voices')
