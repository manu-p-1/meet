from markupsafe import Markup
from wtforms import BooleanField
from wtforms.widgets.core import html_params


class InlineButtonWidget(object):
    html = "<button %s>%s</button>"""
    html_params = staticmethod(html_params)

    def __init__(self, input_type='submit'):
        self.input_type = input_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return Markup(self.html % (self.html_params(name=field.name, **kwargs), "Login"))


class InlineSubmitField(BooleanField):
    def __init__(self, label='', validators=None, **kwargs):
        super(InlineSubmitField, self).__init__(label, validators, **kwargs)

    widget = InlineButtonWidget()
