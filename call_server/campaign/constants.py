SEGMENT_BY_LOCATION = 'location'
SEGMENT_BY_CUSTOM = 'custom'
SEGMENT_BY_CHOICES = (
    (SEGMENT_BY_LOCATION, 'Location'),
    (SEGMENT_BY_CUSTOM, 'Custom')
)

LOCATION_POSTAL = 'postal'
LOCATION_ADDRESS = 'address'
LOCATION_LATLON = 'latlon'
LOCATION_DISTRICT = 'district'
LOCATION_CHOICES = (
    ('', 'None'),
    (LOCATION_POSTAL, 'ZIP / Postal Code'),
    (LOCATION_ADDRESS, 'Street Address'),
    (LOCATION_LATLON, 'Lat / Lon'),
    (LOCATION_DISTRICT, 'District')
)

STATUS_ARCHIVED = 0
STATUS_PAUSED = 1
STATUS_LIVE = 2
CAMPAIGN_STATUS = {
    STATUS_ARCHIVED: 'archived',
    STATUS_PAUSED: 'paused',
    STATUS_LIVE: 'live',
}

EMBED_FORM_CHOICES = (
    ('', 'None'),
    ('iframe', 'iFrame'),
    ('custom', 'Custom'),
)

EMBED_SCRIPT_DISPLAY = (
    ('', 'None'),
    ('overlay', 'Overlay'),
    ('replace', 'Replace Form'),
    ('custom', 'Custom')
)


# empty set of choices, for filling in on client-side
EMPTY_CHOICES = {'': ''}

STRING_LEN = 100
TWILIO_SID_LENGTH = 34
