from .forms import BestiaryQuickSearchForm


def quick_search_form(request):
    return {'bestiary_quick_search': BestiaryQuickSearchForm()}
