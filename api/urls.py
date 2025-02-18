from django.urls import path
from .views import LLMProxyView

urlpatterns = [
    path("llm/", LLMProxyView.as_view(), name="llm_proxy"),
]
