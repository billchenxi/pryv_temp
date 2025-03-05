import os
import openai
from openai import OpenAI
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class LLMProxyView(APIView):
    def post(self, request):
        query = request.data.get("message")
        model_name = request.data.get("model", "gpt-3.5-turbo")

        api_key = request.headers.get("Authorization")
        # Validate API key format (should be "Bearer <KEY>")
        if not api_key or not api_key.startswith("Bearer "):
            return Response(
                {"error": "Invalid or missing API key"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Extract API key (remove "Bearer " prefix)
        api_key = api_key.split("Bearer ")[1]

        if not query:
            return Response(
                {"error": "Message field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if model_name in ["gpt-3.5-turbo", "gpt-4"]:
                # OpenAI GPT-3.5/GPT-4
                client = OpenAI(api_key=api_key)
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
