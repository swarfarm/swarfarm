import autocomplete_light
from models import Monster


class MonsterAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    choice_template = 'monster_choice_autocomplete.html'


autocomplete_light.register(
    Monster,
    MonsterAutocomplete,
    choices=Monster.objects.all().order_by('is_awakened', 'element'),
    search_fields=['name', 'awakens_from__name'],
    attrs={
        'placeholder': 'Start typing monster name',
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 6,
    }
)
