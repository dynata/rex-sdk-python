from dynata_rex import OpportunityRegistry

registry = OpportunityRegistry('rex_access_key', 'rex_secret_key')

opportunities = registry.list_opportunities()

opportunity = opportunities[0]

registry.ack_opportunity(opportunity.id)
