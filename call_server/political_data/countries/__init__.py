from flask.ext.babel import gettext as _

class DataProvider(object):
    country_name = None
    campaign_types = []

    def __init__(self, **kwargs):
        pass

    def load_data(self):
        """
        Loads all country-specific data and caches the result
        """
        raise NotImplementedError()

    def get_location(self, locate_by, raw):
        """
        @return  a location within the country using the given raw input
        """
        raise NotImplementedError()

    @property
    def campaign_type_choices(self):
        return [(key, campaign_type.type_name) for key, campaign_type in self.campaign_types]

    def get_campaign_type(self, type_id):
        type_class = dict(self.campaign_types).get(type_id)
        return type_class(self)

    def cache_get(self, key, default=list()):
        """
        Checks for key in cache and returns it, or default
        This is needed because werkzeug caches don't return defaults like dicts do
        """
        return self._cache.get(key) or default

    def cache_set(self, key, value):
        """ Add a new key/value to the cache """
        if hasattr(self._cache, 'set'):
            self._cache.set(key, value)
        elif hasattr(self._cache, 'update'):
            self._cache.update({key:value})
        else:
            raise AttributeError('cache does not appear to be dict-like')

    def cache_set_many(self, mapping):
        """
        Sets multiple keys and values from a mapping.
        Handles difference between flask-cache and mock-dictionary
        """
        if hasattr(self._cache, 'set_many'):
            self._cache.set_many(mapping)
        elif hasattr(self._cache, 'update'):
            self._cache.update(mapping)
        else:
            raise AttributeError('cache does not appear to be dict-like')

class CampaignType(object):
    type_name = None
    subtypes = []
    target_orders = [
        ('in-order', _("In order"))
    ]

    def __init__(self, data_provider):
        self.data_provider = data_provider

    @property
    def region_choices(self):
        """
        @return  a list of political regions for this campaign type
        """
        return []

    def all_targets(self, location, campaign_region=None):
        """
        Find all targets for a location, crossing political boundaries if
        necessary.
        @return  a dictionary of target uids grouped by subtype.
        """
        raise NotImplementedError()

    def sort_targets(self, targets, subtype, order):
        """
        Sort and filter a dictionary of targets (grouped by subtype), as
        returned from all_targets, based on the provided subtype and order.
        @return  a list of sorted and filtered target uids
        """
        raise NotImplementedError()

    @property
    def country_name(self):
        return self.data_provider.country_name

    @property
    def subtype_choices(self):
        return CampaignType.subtypes + self.subtypes

    def get_subtype_display(self, subtype, campaign_region=None):
        choices_dict = dict(self.subtype_choices)
        return choices_dict.get(subtype, None)

    @property
    def target_order_choices(self):
        return CampaignType.target_orders + self.target_orders

    def get_order_display(self, target_order):
        choices_dict = dict(self.target_order_choices)
        return choices_dict.get(target_order, None)

    def get_targets_for_campaign(self, location, campaign):
        country_code = campaign.country_code
        if isinstance(location, basestring):
            location = self.data_provider.get_location(campaign.locate_by, location)
        all_targets = self.all_targets(location, campaign.campaign_state)
        return self.sort_targets(all_targets, campaign.campaign_subtype, campaign.target_ordering)
