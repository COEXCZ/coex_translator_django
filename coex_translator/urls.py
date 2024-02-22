from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from coex_translator.views import PublishWebhookView

app_name = 'coex_translator'

urlpatterns = [
    path('publish-webhook/', csrf_exempt(PublishWebhookView.as_view()), name='publish_webhook'),
]
