import autocomplete_light
from models import Monster, MonsterInstance


class MonsterAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    model = Monster
    search_fields = ['name', 'awakens_from__name', 'awakens_to__name', '^element']
    split_words = True
    choice_template = 'autocomplete/monster_choice.html'
    limit_choices = 15
    attrs = {
        'placeholder': 'Start typing monster name',
        'data-autocomplete-minimum-characters': 2,
    }

    def choices_for_request(self):
        self.choices = self.choices.order_by('element', 'is_awakened')
        return super(MonsterAutocomplete, self).choices_for_request()

autocomplete_light.register(MonsterAutocomplete)


class MonsterInstanceAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    model = MonsterInstance
    search_fields = ['monster__name', 'monster__awakens_from__name', 'monster__awakens_to__name', '^monster__element']
    split_words = True
    choice_template = 'autocomplete/monster_instance_choice.html'
    limit_choices = 15
    attrs = {
        'placeholder': 'Start typing monster name',
        'data-autocomplete-minimum-characters': 2,
    }

    def choices_for_request(self):
        self.choices = self.choices.filter(owner=self.request.user.summoner)
        return super(MonsterInstanceAutocomplete, self).choices_for_request()

autocomplete_light.register(MonsterInstanceAutocomplete)
