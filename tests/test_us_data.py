import logging

from run import BaseTestCase

from call_server.political_data.lookup import locate_targets
from call_server.political_data.countries.us import USDataProvider
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
        self.CONGRESS_CAMPAIGN = Campaign(
            country_code='us',
            campaign_type='congress',
            campaign_subtype='both',
            target_ordering='in-order',
            locate_by='postal')

    def test_cache(self):
        self.assertIsNotNone(self.mock_cache)
        self.assertIsNotNone(self.us_data)

    def test_districts(self):
        district = self.us_data.get_districts('94612')[0]
        self.assertEqual(district['state'], 'CA')
        self.assertEqual(district['house_district'], '13')

    def test_district_multiple_states(self):
        districts = self.us_data.get_districts('53811')
        # apparently this zipcode is in multiple states
        self.assertEqual(len(districts), 4)

    def test_senate(self):
        senator_0 = self.us_data.get_senators('CA')[0]
        self.assertEqual(senator_0['chamber'], 'senate')
        self.assertEqual(senator_0['state'], 'CA')

        senator_1 = self.us_data.get_senators('CA')[1]
        self.assertEqual(senator_1['chamber'], 'senate')
        self.assertEqual(senator_1['state'], 'CA')

        # make sure we got two different senators...
        self.assertNotEqual(senator_0['last_name'], senator_1['last_name'])

    def test_house(self):
        rep = self.us_data.get_house_members('CA', '13')[0]
        self.assertEqual(rep['chamber'], 'house')
        self.assertEqual(rep['state'], 'CA')
        self.assertEqual(rep['district'], '13')

    def test_dc(self):
        no_senators = self.us_data.get_senators('DC')
        self.assertEqual(no_senators, [])

        rep = self.us_data.get_house_members('DC', '0')[0]
        self.assertEqual(rep['chamber'], 'house')
        self.assertEqual(rep['state'], 'DC')
        self.assertEqual(rep['district'], '0')

    def test_locate_targets(self):
        location = Location({'zipcode': '05055'})
        uids = locate_targets(location, self.CONGRESS_CAMPAIGN, self.mock_cache)
        # returns a list of target uids
        self.assertEqual(len(uids), 3)

        house_rep = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(house_rep['chamber'], 'house')
        self.assertEqual(house_rep['state'], 'VT')

        senator_0 = self.us_data.get_uid(uids[1])[0]
        self.assertEqual(senator_0['chamber'], 'senate')
        self.assertEqual(senator_0['state'], 'VT')

        senator_1 = self.us_data.get_uid(uids[2])[0]
        self.assertEqual(senator_1['chamber'], 'senate')
        self.assertEqual(senator_1['state'], 'VT')

    def locate_targets_house_only(self):
        self.CONGRESS_CAMPAIGN.campaign_subtype = 'lower'
        location = Location({'zipcode': '05055'})
        uids = locate_targets(location, self.CONGRESS_CAMPAIGN, self.mock_cache)
        self.assertEqual(len(uids), 1)

        first = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(first['chamber'], 'house')

    def locate_targets_senate_only(self):
        self.CONGRESS_CAMPAIGN.campaign_subtype = 'upper'
        location = Location({'zipcode': '05055'})

        uids = locate_targets(location, self.CONGRESS_CAMPAIGN, self.mock_cache)
        self.assertEqual(len(uids), 2)

        first = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(first['chamber'], 'senate')

        second = self.us_data.get_uid(uids[1])[0]
        self.assertEqual(second['chamber'], 'senate')

    def test_locate_targets_both_ordered_house_first(self):
        self.CONGRESS_CAMPAIGN.campaign_subtype = 'both'
        self.CONGRESS_CAMPAIGN.target_ordering = 'lower-first'
        location = Location({'zipcode': '05055'})

        uids = locate_targets(location, self.CONGRESS_CAMPAIGN, self.mock_cache)
        self.assertEqual(len(uids), 3)

        first = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(first['chamber'], 'house')

        second = self.us_data.get_uid(uids[1])[0]
        self.assertEqual(second['chamber'], 'senate')

        third = self.us_data.get_uid(uids[2])[0]
        self.assertEqual(third['chamber'], 'senate')

    def test_locate_targets_both_ordered_senate_first(self):
        self.CONGRESS_CAMPAIGN.campaign_subtype = 'both'
        self.CONGRESS_CAMPAIGN.target_ordering = 'upper-first'
        location = Location({'zipcode': '05055'})

        uids = locate_targets(location, self.CONGRESS_CAMPAIGN, self.mock_cache)
        self.assertEqual(len(uids), 3)

        first = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(first['chamber'], 'senate')

        second = self.us_data.get_uid(uids[1])[0]
        self.assertEqual(second['chamber'], 'senate')

        third = self.us_data.get_uid(uids[2])[0]
        self.assertEqual(third['chamber'], 'house')
