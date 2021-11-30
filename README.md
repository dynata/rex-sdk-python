# rex-sdk-python

Package for building and interacting with the Dynata Respondent Exchange (REX)

&nbsp;  

## Quickstart:

&nbsp;  

### *__Opportunity Registry__*
### Instantiate a Registry Client
```
from dynata_rex import OpportunityRegistry
registry = OpportunityRegistry('rex_access_key', 'rex_secret_key')
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

### Instantiate a RespondentGateway Client
```
from dynata_rex import RespondentGateway
gateway = RespondentGateway('rex_access_key', 'rex_secret_key')
```

### Create a survey link for your respondent
```
url = 'https://respondent.fake.rex.dynata.com/start?ctx=XXXX&language=en'

signed_link = gateway.create_respondent_url(url,
                                            '1990-01-01',
                                            'male',
                                            '90210',
                                            'very-unique-respondent-id',
                                            ttl=60)
# https://respondent.fake.rex.dynata.com/start?ctx=XXXX&language=en&birth_date=1990-01-01&gender=male&postal_code=90210&respondent_id=very-unique-respondent-id&access_key=rex_access_key&expiration=2021-11-29T15:35:12.993Z&signature=4353e8c4ca8f8fb75530214ac78139b55ca3f090438c639476b8584afe1396e6
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
end_url = "https://respondent.fake.rex.dynata.com/end?ctx=XXXX&transaction_id=123456&disposition=2&status=1&access_key=rex_access_key&expiration=2021-11-24T19:23:23.439Z&signature=d351ff102b3ae6252d47fd54b859ecaf38c2701f214c233848bbdf64c0bc7fe1"

gateway.verify_url(end_url)

# True
```
##### Missing Signature
```
missing_signature = "https://respondent.fake.rex.dynata.com/end?ctx=XXXX&transaction_id=123456&disposition=2&status=1&access_key=rex_access_key&expiration=2021-11-24T19:23:23.439Z"

gateway.verify_url(missing_signature)

# False
```
##### Altered Parameters (Term --> Complete Attempt)
```
# Disposition changed to 1 (from 2) and status to 0 (from 1)

altered_parameters = "https://respondent.fake.rex.dynata.com/end?ctx=XXXX&transaction_id=123456&disposition=1&status=0&access_key=rex_access_key&expiration=2021-11-24T19:23:23.439Z&signature=d351ff102b3ae6252d47fd54b859ecaf38c2701f214c233848bbdf64c0bc7fe1"

gateway.verify_url(altered_parameters)

# False
```
##### Get Disposition of a Survey from Endlink
```
termination = "https://respondent.fake.rex.dynata.com/end?ctx=XXXX&transaction_id=123456&disposition=2&status=1&access_key=rex_access_key&expiration=2021-11-24T19:23:23.439Z&signature=d351ff102b3ae6252d47fd54b859ecaf38c2701f214c233848bbdf64c0bc7fe1"

disposition = gateway.get_respondent_disposition(termination)

# <GatewayDispositionsEnum.TERMINATION: 2>

disposition.name

# 'TERMINATION'

disposition.value

# 2
```

##### Get Disposition + Status of a Survey from Endlink
```
termination = "https://respondent.fake.rex.dynata.com/end?ctx=XXXX&transaction_id=123456&disposition=2&status=1&access_key=rex_access_key&expiration=2021-11-24T19:23:23.439Z&signature=d351ff102b3ae6252d47fd54b859ecaf38c2701f214c233848bbdf64c0bc7fe1"

status = gateway.get_respondent_status(termination)

#<GatewayStatusEnum.TERMINATION_DYNATA: (<GatewayDispositionsEnum.TERMINATION: 2>, 1)>

status.name

# 'TERMINATION_DYNATA'

status.value

# (<GatewayDispositionsEnum.TERMINATION: 2>, 1)
```

##### Create a context
```
context_id = 'super-unique-ctx-id'
data = {
    'ctx': 'parent-context-id',           # From survey link 'ctx' parameter
    'gender': 'male',
    'birth_data': '1999-09-09',
    'postal_code': '90210'
}
gateway.create_context(context_id, data)

# 'super-unique-ctx-id'
```

##### Retrieve a context
```
gw.get_context('super-unique-ctx-id')

# {
#    'id': 'super-unique-ctx-id', 
#    'items': {
#        'ctx': 'parent-context-id',
#        'gender': 'male',
#        'birth_data': '1999-09-09',
#        'postal_code': '90210'
#     }
# }
```

##### Expire a context
```
gw.expire_context('super-unique-ctx-id')

# {
#    'id': 'super-unique-ctx-id', 
#    'items': {
#        'ctx': 'parent-context-id',
#        'gender': 'male',
#        'birth_data': '1999-09-09',
#        'postal_code': '90210'
#     },
#     'expiration': '2021-11-30T16:10:44Z'
# }
```


