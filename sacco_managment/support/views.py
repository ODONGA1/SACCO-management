from django.utils.translation import gettext as _
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import openai





# Set OpenAI API key from settings
openai.api_key = settings.OPENAI_API_KEY


def faq(request):
    return render(request, "faq/faq.html", {
        "breadcrumb": {"parent": "FAQ", "child": "FAQ"}
    })


def tutorial(request):
    return render(request, "support/tutorial.html", {
        "breadcrumb": {"parent": "Support", "child": "Tutorial"}
    })


@csrf_exempt  # Keep this ONLY if you're manually handling CSRF via JS (as you are)
def chatbot(request):
    """
    POST  => returns JSON response from GEMS AI
    GET   => renders chat UI
    """
    if request.method == "POST":
        message = request.POST.get("message", "").strip()

        if not message:
            return JsonResponse({"reply": "Please type a message to continue."})

        try:
            # Call OpenAI's ChatCompletion API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are GEMS AI, Gem SACCO’s virtual assistant. "
                            "Help users understand accounts, KYC, loans, savings, "
                            "mobile money, crypto wallets and general support. "
                            "Be friendly, concise, and NEVER give legal advice."
                        )
                    },
                    {"role": "user", "content": message}
                ]
            )
            reply = response.choices[0].message["content"]
        except Exception as e:
            print("OpenAI Error:", e)
            reply = "GEMS AI is not available at the moment. Please try again later."

        return JsonResponse({"reply": reply})

    # If GET request → show the chatbot interface
    return render(request, "support/chatbot.html")
