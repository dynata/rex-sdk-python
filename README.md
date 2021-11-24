# rex-sdk-python

Package for building and interacting with the Dynata Respondent Exchange (REX)

&nbsp;  

## Quickstart:

&nbsp;  

### *__Opportunity Registry__*

&nbsp;  

### Instantiate a Registry Client
```
from dynata_rex import RegistryAPI
registry = RegistryAPI('rex_access_key', 'rex_secret_key', 'registry_base_url')
```
### List opportunities from the registry
```
opportunities = registry.list_opportunities()

# [Opportunity(id=1,...), Opportunity(id=2,...), Opportunity(id=1,...)]
```
### Convert an opportunity to JSON
```
opportunity_json = Opportunity.json()
```
### Acknowledge a list of opportunities from the registry
```
registry.ack_opportunities([opportunity_1.id, ..., opportunity_N.id])
```
### Acknowledge a single opportunity from the registry
```
registry.ack_opportunity(opportunity.id)
```
### Get a list of corresponding opportunities from a project_id
```
corresponding = registry.list_project_opportunities(opportunity.project_id)

# [12345, 45678, 78901]
```
### Download a collection from a collection-type targeting cell
```
data = registry.download_collection(cell.collection_id)
```  

&nbsp;  
&nbsp;  

### *__Respondent Gateway__*

&nbsp;  

### Instantiate a RespondentGateway Client
```
from dynata_rex import RespondentGateway
gateway = RespondentGateway('rex_access_key', 'rex_secret_key')
```
### Sign an inbound /start link with your credentials
```
url = 'https://respondent.fake.rex.dynata.com/start?ctx=XXXX&language=en'
signed_url = gateway.sign_url(url)

# "https://respondent.fake.rex.dynata.com/start?ctx=XXXX&language=en&access_key=rex_access_key&expiration=2021-11-24T16:12:06.070Z&signature=fa8b5cac82d34bcf8026904b353349db5b1b871f735e07a601389cb6da2d744d"
```
### Generate a URL-quoted signed url
```
signed_url = gateway.sign_url(url, url_quoting=True)

# 'https://respondent.fake.rex.dynata.com/start?ctx=XXXX&language=en&access_key=rex_access_key&expiration=2021-11-24T16%3A12%3A35.991Z&signature=4219cf63406ae429d94dbe9c33027816c264c1e2bf1edbadd2510eb9bf2351c3'
```
### Verify a signed /end link URL with your credentials
##### Valid URL
```
# Termination Endlink
end_url = "https://respondent.fake.rex.dynata.com/end?ctx=XXXX&transaction_id=123456disposition=2&status=1&access_key=rex_access_key&expiration=2021-11-24T16:50:53.899Z&signature=15da726b7802bda810c059ee1604f8fd1237a0618c29185c6b16f09e14242278"

gateway.verify_url(end_url)

# True
```
##### Missing Signature
```
missing_signature = "https://respondent.fake.rex.dynata.com/end?ctx=XXXX&transaction_id=123456disposition=2&status=1&access_key=rex_access_key&expiration=2021-11-24T16:50:53.899Z"

gateway.verify_url(missing_signature)

# False
```
##### Altered Parameters (Term --> Complete Attempt)
```
# Disposition changed to 1 (from 2) and status to 0 (from 1)

altered_parameters = "https://respondent.fake.rex.dynata.com/end?ctx=XXXX&transaction_id=123456disposition=1&status=0&access_key=rex_access_key&expiration=2021-11-24T16:50:53.899Z&signature=15da726b7802bda810c059ee1604f8fd1237a0618c29185c6b16f09e14242278"

gateway.verify_url(altered_parameters)

# False
```

