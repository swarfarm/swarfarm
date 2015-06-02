import autocomplete_light
from models import Monster

autocomplete_light.register(
    Monster,
    search_fields=['name'],
    attrs={
        'placeholder': 'Start typing monster name',
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 8,
    }
)
