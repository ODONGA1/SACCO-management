from django.shortcuts import render

# Create your views here.
def faq(request):
    context = {
        "breadcrumb": {
            "parent": "FAQ",
            "child": "FAQ"
        }
    }
    return render(request, 'faq/faq.html', context)



def tutorial(request):
    context = {
        "breadcrumb": {
            "parent": "Support",
            "child": "Tutorial"
        }
    }
    return render(request, 'support/tutorial.html', context)