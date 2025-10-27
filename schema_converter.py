import json
from crdclib import crdclib

yamlfile = 'ruleset_schema.yml'
schemafile = 'ruleset_schema.json'
#yamlfile = 'ExperimentalRuleSet.yml'
#schemafile = 'ExperimentalRuleSet.json'
jsonthing = crdclib.readYAML(yamlfile)
with open(schemafile, 'w') as f:
    json.dump(jsonthing, f, indent=4)
