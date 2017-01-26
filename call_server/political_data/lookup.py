from ..extensions import cache

def locate_targets(location, campaign, cache=cache):
    """
    Convenience method to get targets for location in a given campaign.
    @return  list of target uids
    """

    if campaign.target_set:
        target_set = [t.uid for t in campaign.target_set]
        if campaign.order == 'shuffle':
            random.shuffle(target_set)
        return target_set
    else:
        campaign_data = campaign.get_campaign_data(cache)
        return campaign_data.get_targets_for_campaign(location, campaign)
