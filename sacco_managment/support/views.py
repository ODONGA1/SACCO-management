from django.utils.translation import gettext as _
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
import openai
import logging


# Set OpenAI API key from settings
openai.api_key = settings.OPENAI_API_KEY


logger = logging.getLogger(__name__)


def faq(request):
    return render(request, "faq/faq.html", {
        "breadcrumb": {"parent": "FAQ", "child": "FAQ"}
    })


def tutorial(request):
    return render(request, "support/tutorial.html", {
        "breadcrumb": {"parent": "Support", "child": "Tutorial"}
    })


@csrf_exempt
def chatbot(request):
    """
    Combined view handling:
    - GET: Renders chat interface (support/chatbot.html)
    - POST: Processes chat messages with GEMS AI
    """
    if request.method == "POST":
        # Rate limiting (5 requests per minute)
        ip = request.META.get('REMOTE_ADDR')
        cache_key = f"chatbot_{ip}"
        if cache.get(cache_key, 0) >= 20:
            return JsonResponse({
                'reply': _("Please wait a moment before sending more messages"),
                'status': 'rate_limited'
            }, status=429)
        cache.incr(cache_key, timeout=60)

        message = request.POST.get("message", "").strip()
        lang = request.POST.get("lang", "en")  # New language parameter

        if not message:
            return JsonResponse({
                'reply': _("Please type a message to continue"),
                'status': 'empty_message'
            })

        try:
            # Language-specific system prompts
            system_prompts = {
                'en': _("You are GEMS AI, Gem SACCO's virtual assistant..."),
                'lg': _("Oli GEMS AI, omuyambi wa Gem SACCO..."),
                'fr': _("Vous êtes GEMS AI, l'assistant virtuel..."),
                'sw': _("Wewe ni GEMS AI, msaidizi wa Gem SACCO...")
            }

            response = openai.ChatCompletion.create(
                model=getattr(settings, 'OPENAI_MODEL', "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": system_prompts.get(lang, 'en')
                    },
                    {"role": "user", "content": message}
                ],
                temperature=0.7
            )
            reply = response.choices[0].message["content"]
            
            return JsonResponse({
                'reply': reply,
                'status': 'success'
            })

        except Exception as e:
            logger.error(f"Chatbot error: {str(e)}", exc_info=True)
            return JsonResponse({
                'reply': _("GEMS AI is not available at the moment. Please try again later."),
                'status': 'error'
            }, status=500)

    # GET request - render chat interface
    return render(request, "support/chatbot.html", {
        'default_lang': request.COOKIES.get('gemsai_lang', 'en')
    })