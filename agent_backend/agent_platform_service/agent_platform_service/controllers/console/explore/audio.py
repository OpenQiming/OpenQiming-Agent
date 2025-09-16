import logging

from flask import request
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
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.explore.wraps import InstalledAppResource
from agent_platform_service.services.audio_service import AudioService


class ChatAudioApi(InstalledAppResource):
    def post(self, app_model):
        file = request.files['file']

        try:
            response = AudioService.transcript_asr(
                app_model=app_model,
                file=file,
                end_user=None
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
        except Exception:
            logging.exception("internal server error.")
            raise InternalServerError()


class ChatTextApi(InstalledAppResource):
    def post(self, app_model):
        try:
            response = AudioService.transcript_tts(
                app_model=app_model,
                text=request.form['text'],
                voice=request.form['voice'] if request.form.get(
                    'voice') else app_model.app_model_config.text_to_speech_dict.get('voice'),
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
        except Exception:
            logging.exception("internal server error.")
            raise InternalServerError()


api.add_resource(ChatAudioApi, '/explore-apps/<uuid:installed_app_id>/audio-to-text', endpoint='installed_app_audio')
api.add_resource(ChatTextApi, '/explore-apps/<uuid:installed_app_id>/text-to-audio', endpoint='installed_app_text')
