# rex-sdk-python

Package for building and interacting with the Dynata Respondent Exchange (REX)

## Quickstart:

### Opportunity Registry
#### Instantiate a Registry Client
```
>>> from dynata_rex import RegistryAPI
>>> registry = RegistryAPI(<rex_access_key>, <rex_secret_key>, <registry_base_url>)
```
### List opportunities from the registry
```
>>> opportunities = registry.list_opportunities()
[Opportunity(id=1,...), Opportunity(id=2,...), Opportunity(id=1,...)]
```
### Convert an opportunity to JSON
```
opportunity_json = Opportunity.json()
```
### Acknowledge a list of opportunities from the registry
```
>>> registry.ack_opportunities([opportunity_1.id, ..., opportunity_N.id])
```
### Acknowledge a single opportunity from the registry
```
>>> registry.ack_opportunity(opportunity.id)
```
### Get a list of corresponding opportunities from a project_id
```
>>> corresponding = registry.list_project_opportunities(opportunity.project_id)
```
### Download a collection from a collection-type targeting cell
```
>>> data = registry.download_collection(cell.collection_id)
```