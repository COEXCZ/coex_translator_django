import json

from django.http import HttpResponseForbidden, HttpResponse
from django.views.generic import View

from coex_translator.app_settings import app_settings
from coex_translator.publisher import TranslationAMQPPublisher


class PublishWebhookView(View):

    def check_auth_header(self):
        webhook_secret = app_settings.get('WEBHOOK_SECRET')
        if not webhook_secret:
            return True
        auth_header = self.request.META.get('HTTP_X_AUTHORIZATION')
        if not auth_header:
            return False

        return auth_header == f'Bearer {webhook_secret}'

    def dispatch(self, request, *args, **kwargs):
        if not self.check_auth_header():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def put(self, request):
        if json.loads(request.body).get('message') == TranslationAMQPPublisher.TRANSLATION_UPDATE_MESSAGE:
            TranslationAMQPPublisher.publish_update_translations()
            return HttpResponse()
        return HttpResponseForbidden()
