from markupsafe import Markup
from wtforms import Field
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
        return Markup(self.html % (self.html_params(name=field.name, **kwargs), field.btn_text))


class InlineSubmitField(Field):
    widget = InlineButtonWidget()

    def __init__(self, label='', validators=None, btn_text='Submit', **kwargs):
        super(InlineSubmitField, self).__init__(label, validators, **kwargs)
        self.btn_text = btn_text

    def _value(self):
        if self.data:
            return u''.join(self.data)
        else:
            return u''
