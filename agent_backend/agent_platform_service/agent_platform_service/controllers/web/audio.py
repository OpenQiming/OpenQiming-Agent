import logging

from flask import request
from werkzeug.exceptions import InternalServerError

from agent_platform_basic.exceptions.controllers.web import (
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
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_core.models.db_model.model import App
from agent_platform_service.controllers.web import api
from agent_platform_service.controllers.web.wraps import WebApiResource
from agent_platform_service.services.audio_service import AudioService


class AudioApi(WebApiResource):
    def post(self, app_model: App, end_user):
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
            logging.exception(f"internal server error: {str(e)}")
            raise InternalServerError()


class TextApi(WebApiResource):
    def post(self, app_model: App, end_user):
        try:
            response = AudioService.transcript_tts(
                app_model=app_model,
                text=request.form['text'],
                end_user=end_user.external_user_id,
                voice=request.form['voice'] if request.form.get('voice') else None,
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
            logging.exception(f"internal server error: {str(e)}")
            raise InternalServerError()


api.add_resource(AudioApi, '/audio-to-text')
api.add_resource(TextApi, '/text-to-audio')
