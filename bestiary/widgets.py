from itertools import chain

from django.forms import widgets
from django.utils.encoding import force_text


class AdvancedSelectMultipleWidget(widgets.SelectMultiple):
    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        default = (None, [], 0)
        groups = [default]
        has_selected = False

        for option_value, option_label, option_object in chain(self.choices):
            if option_value is None:
                option_value = ''

            if isinstance(option_label, (list, tuple)):
                index = groups[-1][2] + 1
                subindex = 0
                subgroup = []
                groups.append((option_value, subgroup, index))
                choices = option_label
            else:
                index = len(default[1])
                subgroup = default[1]
                subindex = None
                choices = [(option_value, option_label, option_object)]

            for subvalue, sublabel, subobj in choices:
                selected = (
                    force_text(subvalue) in value and
                    (has_selected is False or self.allow_multiple_selected)
                )
                if selected is True and has_selected is False:
                    has_selected = True
                subgroup.append(self.create_option(
                    name, subvalue, sublabel, selected, index,
                    subindex=subindex, attrs=attrs, instance=subobj
                ))
                if subindex is not None:
                    subindex += 1
        return groups

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None, instance=None):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        if attrs is None:
            attrs = {}
        option_attrs = self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        if selected:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            option_attrs['id'] = self.id_for_label(option_attrs['id'], index)
        return {
            'name': name,
            'value': value,
            'label': label,
            'selected': selected,
            'index': index,
            'attrs': option_attrs,
            'type': self.input_type,
            'template_name': self.option_template_name,
            'instance': instance,
        }


class ElementSelectMultipleWidget(widgets.SelectMultiple):
    option_template_name = 'widgets/select2_element_option.html'

class RuneTypeSelectMultipleWidget(widgets.SelectMultiple):
    option_template_name = 'widgets/select2_runetype_option.html'

class EffectSelectMultipleWidget(AdvancedSelectMultipleWidget):
    option_template_name = 'widgets/select2_effect_option.html'
