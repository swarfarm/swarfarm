from autocomplete_light import shortcuts as autocomplete_light
from bestiary.models import Monster


class BestiaryLinkAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    model = Monster
    search_fields = ['name', 'awakens_from__name', 'awakens_to__name', '^element']
    split_words = True
    choice_template = 'autocomplete/bestiary_link.html'
    limit_choices = 15
    attrs = {
        'placeholder': 'Quick search...',
        'data-autocomplete-minimum-characters': 2,
    }

    def choices_for_request(self):
        self.choices = self.choices.filter(obtainable=True).order_by('element', 'is_awakened')
        return super(BestiaryLinkAutocomplete, self).choices_for_request()

autocomplete_light.register(BestiaryLinkAutocomplete)