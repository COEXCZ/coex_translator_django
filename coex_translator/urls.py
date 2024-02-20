from django.urls import path

from coex_translator.views import PublishWebhookView

app_name = 'coex_translator'

urlpatterns = [
    path('publish-webhook/', PublishWebhookView.as_view(), name='publish_webhook'),
]
