from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, SubmitField, TextField,
                     SelectField, SelectMultipleField,
                     BooleanField, RadioField, IntegerField,
                     FileField, FieldList, FormField)
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms_components import PhoneNumberField, read_only
from wtforms.widgets import TextArea
from wtforms.validators import Required, Optional, AnyOf, NumberRange, ValidationError

from .constants import (SEGMENT_BY_CHOICES, LOCATION_CHOICES,
                        CAMPAIGN_STATUS, EMBED_FORM_CHOICES, EMBED_SCRIPT_DISPLAY)

from .models import Campaign, TwilioPhoneNumber

from ..political_data import COUNTRY_CHOICES
from ..utils import choice_items, choice_keys, choice_values, choice_values_flat


class DisabledSelectField(SelectField):
  def __call__(self, *args, **kwargs):
    kwargs.setdefault('disabled', True)
    return super(DisabledSelectField, self).__call__(*args, **kwargs)


class CountryForm(Form):
    country_type = SelectField(_('Select Country'), validators=[Required()])
    submit = SubmitField(_('Next'))


class TargetForm(Form):
    order = IntegerField(_('Order'),)
    title = TextField(_('Title'), [Optional()])
    name = TextField(_('Name'), [Required()])
    number = PhoneNumberField(_('Phone Number'), [Required()])
    uid = TextField(_('Unique ID'), [Optional()])


class CampaignForm(Form):
    next = HiddenField()
    name = TextField(_('Campaign Name'), [Required()])
    campaign_country = DisabledSelectField(_("Country"), [Optional()], choices=COUNTRY_CHOICES)
    campaign_type = DisabledSelectField(_("Type"), [Optional()])
    campaign_state = SelectField(_('State'), [Optional()])
    campaign_subtype = SelectField(_('Subtype'), [Optional()])
    # nested_type passed to data-field in template, but starts empty

    segment_by = RadioField(_('Segment By'), [Required()], choices=choice_items(SEGMENT_BY_CHOICES),
                            description=True, default=SEGMENT_BY_CHOICES[0][0])
    locate_by = RadioField(_('Locate By'), [Optional()], choices=choice_items(LOCATION_CHOICES),
                           description=True, default=None)
    target_set = FieldList(FormField(TargetForm, _('Choose Targets')), validators=[Optional()])
    target_ordering = RadioField(_('Order'), [Optional()], description=True)

    call_limit = BooleanField(_('Limit Maximum Calls'), [Optional()], default=False)
    call_maximum = IntegerField(_('Call Maximum'), [Optional(), NumberRange(min=0)])

    phone_number_set = QuerySelectMultipleField(_('Select Phone Numbers'),
                                                query_factory=TwilioPhoneNumber.available_numbers,
                                                validators=[Required()])
    allow_call_in = BooleanField(_('Allow Call In'))

    submit = SubmitField(_('Edit Audio'))

    def __init__(self, campaign_data, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)

        read_only(self.campaign_country)
        read_only(self.campaign_type)

        self.campaign_type.choices = choice_items(campaign_data.data_provider.campaign_type_choices)
        self.campaign_state.choices = choice_items(campaign_data.region_choices)
        self.campaign_subtype.choices = choice_items(campaign_data.subtype_choices)
        self.target_ordering.choices = choice_items(campaign_data.target_order_choices)

    def validate(self):
        # check default validation
        if not Form.validate(self):
            return False

        # check nested forms
        for t in self.target_set:
            if not t.form.validate():
                error_fields = ','.join(t.form.errors.keys())
                self.target_set.errors.append({'target': t.name, 'message': 'Invalid target ' + error_fields})
                return False

        return True


class CampaignAudioForm(Form):
    next = HiddenField()
    msg_intro = TextField(_('Introduction'))
    msg_intro_confirm = TextField(_('Start Confirmation'))
    msg_location = TextField(_('Location Prompt'))
    msg_intro_location = TextField(_('Introduction with Location'))
    msg_invalid_location = TextField(_('Invalid Location'))
    msg_unparsed_location = TextField(_('Unparsed Location'))
    msg_choose_target = TextField(_('Choose Target'))
    msg_call_block_intro = TextField(_('Call Block Introduction'))
    msg_target_intro = TextField(_('Target Introduction'))
    msg_target_busy = TextField(_('Target Busy'))
    msg_between_calls = TextField(_('Between Calls'))
    msg_final_thanks = TextField(_('Final Thanks'))

    submit = SubmitField(_('Save and Test'))


class AudioRecordingForm(Form):
    key = TextField(_('Key'), [Required()])
    file_storage = FileField(_('File'), [Optional()])
    text_to_speech = FileField(_('Text to Speech'), [Optional()])
    description = TextField(_('Description'), [Optional()])


class CampaignLaunchForm(Form):
    next = HiddenField()

    test_call_number = TextField(_('Call Me'))
    test_call_location = TextField(_('Test Location'))

    # standard embed fields
    embed_script = TextField(_('Display Script'), widget=TextArea(), description=True)
    embed_code = TextField(_('Embed Code'), widget=TextArea(), description=True)
    embed_type = SelectField(_('Form Embed'), [Optional()], choices=choice_items(EMBED_FORM_CHOICES),
        description=True, default=EMBED_FORM_CHOICES[0][0])

    # custom embed fields
    embed_form_sel = TextField(_('Form Selector'))
    embed_phone_sel = TextField(_('Phone Field'))
    embed_location_sel = TextField(_('Location Field'))
    embed_custom_css = TextField(_('Custom CSS URL'))
    embed_script_display = SelectField(_('Script Display'), [Optional()], choices=choice_items(EMBED_SCRIPT_DISPLAY),
        description=True, default=EMBED_SCRIPT_DISPLAY[0][0])
    embed_custom_js = TextField(_('Custom JS Code'), description=True)

    submit = SubmitField(_('Launch'))


class CampaignStatusForm(Form):
    status_code = RadioField(_("Status"), [AnyOf([str(val) for val in CAMPAIGN_STATUS.keys()])],
                             choices=[(str(val), label) for val, label in CAMPAIGN_STATUS.items()])
    submit = SubmitField(_('Save'))
