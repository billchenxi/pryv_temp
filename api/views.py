import os
import openai
from openai import OpenAI
import anthropic
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
# import logging
# from groq import Groq

class LLMProxyView(APIView):
    authentication_classes = []  # Disable Django authentication
    permission_classes = [AllowAny]  # Allow all requests
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
            if model_name in [
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4o",
                "gpt-4.5-preview",  # not available yet
                "o1",  # too expensive and slow
                "o3-mini",
                "o1-mini",
            ]:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model_name, messages=[{"role": "user", "content": query}]
                )
                reply = response.choices[0].message.content.strip()

            elif model_name in ["claude-3-5-sonnet", "claude-3-opus"]:
                # Anthropic's Claude
                anthropic_client = anthropic.Anthropic(api_key=api_key)
                response = anthropic_client.messages.create(
                    system="You are a world-class AI assistant.",
                    model=(
                        model_name + "-20240620"
                        if model_name == "claude-3-5-sonnet"
                        else model_name + "-20240229"
                    ),
                    messages=[
                        {"role": "user", "content": [{"type": "text", "text": query}]}
                    ],
                    max_tokens=1000,
                )
                reply = response.content[0].text

            elif model_name in ["llama"]:
                # LLaMA via Kuzco API (non-streaming)
                url = "https://api.kuzco.xyz/v1/chat/completions"
                print(api_key)
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "messages": [{"role": "user", "content": query}],
                    "model": "llama3:latest",
                    "stream": False,
                }

                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    reply = response.json()["choices"][0]["message"]["content"].strip()
                    # logger.info("Received response from LLaMA")
                else:
                    error_message = response.json().get("error", {}).get("message", "")
                    # logger.error(
                    #     f"Error from LLaMA API: {response.status_code}, {error_message}"
                    # )
                    reply = f"Error: {response.status_code}, {error_message}"

            else:
                reply = "Model not supported."

            return Response({"response": reply})

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
