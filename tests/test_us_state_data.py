import logging

from run import BaseTestCase

from call_server.political_data.lookup import locate_targets
from call_server.political_data.countries.us import USDataProvider
from call_server.political_data.constants import US_STATES
from call_server.political_data.geocode import Location
from call_server.campaign.models import Campaign

class TestData(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        # quiet logging
        logging.getLogger('cache').setLevel(logging.WARNING)
        logging.getLogger(__name__).setLevel(logging.WARNING)

        cls.mock_cache = {}  # mock flask-cache outside of application context
        cls.us_data = USDataProvider(cls.mock_cache, 'localmem')
        cls.us_data.load_data()

    def setUp(self):
        self.STATE_CAMPAIGN = Campaign(
            country_code='us',
            campaign_type='state',
            campaign_subtype='both',
            target_ordering='in-order',
            locate_by='latlon')

    def test_cache(self):
        self.assertIsNotNone(self.mock_cache)
        self.assertIsNotNone(self.us_data)

    def test_locate_targets(self):
        location = "37.804417,-122.267747"
        uids = locate_targets(location, self.STATE_CAMPAIGN, self.mock_cache)
        # returns a list of uids (openstates leg_id)
        self.assertEqual(len(uids), 2)

        house_rep = self.us_data.get_state_legid(uids[0])
        self.assertEqual(house_rep['chamber'], 'lower')
        self.assertEqual(house_rep['state'].upper(), 'CA')
        self.assertEqual(house_rep['active'], True)

        senator = self.us_data.get_state_legid(uids[1])
        self.assertEqual(senator['chamber'], 'upper')
        self.assertEqual(senator['state'].upper(), 'CA')
        self.assertEqual(senator['active'], True)

    def test_locate_targets_lower_only(self):
        location = "37.804417,-122.267747"
        self.STATE_CAMPAIGN.campaign_subtype = 'lower'
        uids = locate_targets(location, self.STATE_CAMPAIGN, self.mock_cache)
        self.assertEqual(len(uids), 1)

        print uids

        house_rep = self.us_data.get_state_legid(uids[0])
        self.assertEqual(house_rep['chamber'], 'lower')
        self.assertEqual(house_rep['state'].upper(), 'CA')
        self.assertEqual(house_rep['active'], True)

    def test_locate_targets_upper_only(self):
        location = "37.804417,-122.267747"
        self.STATE_CAMPAIGN.campaign_subtype = 'upper'
        uids = locate_targets(location, self.STATE_CAMPAIGN, self.mock_cache)
        self.assertEqual(len(uids), 1)

        print uids

        senator = self.us_data.get_state_legid(uids[0])
        self.assertEqual(senator['chamber'], 'upper')
        self.assertEqual(senator['state'].upper(), 'CA')
        self.assertEqual(senator['active'], True)

    def test_locate_targets_ordered_lower_first(self):
        location = "37.804417,-122.267747"
        self.STATE_CAMPAIGN.campaign_subtype = 'both'
        self.STATE_CAMPAIGN.target_ordering = 'lower-first'
        uids = locate_targets(location, self.STATE_CAMPAIGN, self.mock_cache)
        self.assertEqual(len(uids), 2)

        first = self.us_data.get_state_legid(uids[0])
        self.assertEqual(first['chamber'], 'lower')

        second = self.us_data.get_state_legid(uids[1])
        self.assertEqual(second['chamber'], 'upper')

    def test_locate_targets_ordered_upper_first(self):
        location = "37.804417,-122.267747"
        self.STATE_CAMPAIGN.campaign_subtype = 'both'
        self.STATE_CAMPAIGN.target_ordering = 'upper-first'
        uids = locate_targets(location, self.STATE_CAMPAIGN, self.mock_cache)
        self.assertEqual(len(uids), 2)

        first = self.us_data.get_state_legid(uids[0])
        self.assertEqual(first['chamber'], 'upper')

        second = self.us_data.get_state_legid(uids[1])
        self.assertEqual(second['chamber'], 'lower')

    def test_locate_targets_incorrect_state(self):
        self.STATE_CAMPAIGN.campaign_state = 'CA'
        location = "42.355662,-71.065483"  # location in Boston
        
        uids = locate_targets(location, self.STATE_CAMPAIGN, self.mock_cache)
        self.assertEqual(len(uids), 0)

    def test_50_governors(self):
        NO_GOV = ['AS', 'GU', 'MP', 'PR', 'VI', 'DC', '']
        for (abbr, state) in US_STATES:
            gov = self.us_data.get_state_governor(abbr)
            if not gov:
                self.assertIn(abbr, NO_GOV)
                continue
            self.assertEqual(len(gov.keys()), 5)
            self.assertEqual(gov['title'], 'Governor')

    def test_ca_governor(self):
        gov = self.us_data.get_state_governor('CA')
        self.assertEqual(gov['first_name'], 'Jerry')
        self.assertEqual(gov['last_name'], 'Brown')
        self.assertEqual(gov['state'], 'CA')
        self.assertEqual(gov['phone'], '916-445-2841')
