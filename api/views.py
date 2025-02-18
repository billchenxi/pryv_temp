import os
import openai
from openai import OpenAI
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

openai_api_key = "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"


class LLMProxyView(APIView):
    def post(self, request):
        query = request.data.get("message")
        model_name = request.data.get("model", "gpt-3.5-turbo")

        if not query:
            return Response(
                {"error": "Message field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if model_name in ["gpt-3.5-turbo", "gpt-4"]:
                # OpenAI GPT-3.5/GPT-4
                client = OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model=model_name, messages=[{"role": "user", "content": query}]
                )
                reply = response.choices[0].message.content.strip()

            else:
                reply = "Model not supported."

            return Response({"response": reply})

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
