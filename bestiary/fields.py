from django.forms import models, fields


class AdvancedModelChoiceIterator(models.ModelChoiceIterator):
    def choice(self, obj):
        return self.field.prepare_value(obj), self.field.label_from_instance(obj), obj


class AdvancedSelectMultiple(models.ModelMultipleChoiceField):
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices

        return AdvancedModelChoiceIterator(self)

    choices = property(_get_choices, fields.ChoiceField._set_choices)
