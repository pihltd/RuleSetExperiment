# CRDC Rule Set Experiment
This repo is exploring how to do conditional validations in CRDC, mainly through developing a stanard to document the conditions.

## Basic rule format
The conditional rules are expressed in YAML format:

conditional_rules:
  NodeName:
    - property_name:
      is: None/NotNone/Match
      then:
        target_node_name:
          - target_property_name:
              scope: global/each
              is: (or isReq)
    - property_name2:
  NodeName2:
    - property_name:
      is:
      then:
        target_node_name:
          - target_property_name:
            scope:
            is:
## Rule elements
**conditional_rules** : The key used to identify the start of the conditional rules. \
**NodeName**: The node where the property with the conditional test resides. \
**property_name**: The property to be tested.  Property names are the start of a list of Python dictionaries. \
**is**:  This is the value to be tested for. \
  - *None* indicates that there should be no value in the property. \
  - *NotNone* indicates that there must be some value in the property, but does not specify a specific value. \
  - Any other value is assumed to be a directive for a direct match in the property. \
**then**: this key starts the collection of targets to be checked. \
**target_node_name**: The node where the property to be tested resides. \
**target_property_name**: The target property to be tested. This will be a list of dictionary. \
**scope**: This term defines how broadly to test.
  - **global**: If the scope is global, then all rows in the target property will be checked
  - **each**: If the scope is each, individual rows corresponding to the *property_name* and *is* statements will be checked.
**is**: the value that should be present in the *target_proprety_name*.  This follows the same rules as the *is* statement for *property_name*
**isReq**:  This is an alternative to *is* and is a boolean indicating if the *target_property_name* is required (True) or not required (False).  This is used to override model-defined required fields or require fields not required in the model
**enum**: This allows for testing the values in the *target_property_name* against a list of possible values.  The test is passed if the value in *target_property_name* matches one of the values in the *enum* list.
NOTE:  Need to look at using enums in the *property_name* value test


## Examples
### Example 1:
If there is a value in the *primary_diagnosis* field, then both the *tumor_grade* and *diagnosis_id* fields are required to have entries.

```YAML
conditional_rules:
  diagnosis:
    - primary_diagnosis:
        is:  NotNone
        then:
          diagnosis:
            - tumor_grade:
                scope: each
                isReq: True
            - diagnosis_id:
                scope: each
                isReq: True
```

**Discussion**
The *primary_diagnosis* field is contained in the *diagnosis* node, so *diagnosis* is the overall key to the data structure and *primary_diagnosis* is the primary key for this entry in the list of tests.  The *is* directive is **NotNone** and should be interpreted as "when there is a value in the *primary_diagnosis* field, perform the checks in the *then* section for this row.

The *then* section outlines that if there is data in the *primary_diagnosis* field, the ```isReq:True``` statement indicates both *tumor_grade* and *diagnosis_id* are now required, regardless of their definition in the original model.  The ```scope: each``` directive indicates that the requirement is applied only to those instances (rows) where there is data in the *primary_diagnosis* field.  Any rows where *primary_diagnosis* has no data would not be required to have data in *tumor_grade* or *diagnosis_id*.

### Example 2:
For project BigData, sample information was not collected, therefore sample_id is not required

```YAML
conditional_rules:
    program:
    - program_short_name:
        is: BigData
        then:
          sample:
            - sample_id:
                scope: global
                is: None
```

**Discussion**
In this example, the underlying assuption is that the model requires *sample_id* to be part of the data.  This rule relaxes that by looking at the *program_short_name* property in the *program* node.  For any data comming from the BigData program, there should be no data (``` is: None```) in the *sample_id* column in any of the rows (```scope: global```) in the *sample* node.  As this rule is written, the system would throw an error if it finds entries in *sample_id* because ```is: None``` specifies that there shouldn't be any value at all.  If the intent is to simply not check if there are values in *sample_id* or not, then ```isReq: False``` would be the preferred rule.

### Example 3:
This example demonstrates requiring specific values in the target, or providing an enum set that the target value must belong to.

```YAML
conditional_rules:
  sample:
    - sample_type_category:
        is: NotNone
        then:
          sample:
            - sample_type_category:
                enum:
                  - 'DNA'
                  - 'RNA'
                scope: each
          genomic_info:
            - reference_genome_assembly:
                is: GRCh38
                scope: each
            - library_selection:
                enum:
                  - 'Restriction Digest'
                  - 'RACE'
                scope: each
```
In this example, the presence of data in the *sample_type_cateogry* of the *sample* node is triggering three different checks, one in the *sample* node and two in the *genomic_info* node.  Two of the tests (*sample_type_category* in teh *sample* node and *library_selection* in the *genomic_info node*) use the *enum* statement in place of the *is* statement.  This means that the value found in the two properties must be a memeber of the enum set.  So for *sample_type_category* the value must be either 'DNA' or 'RNA' and for *library_selection*, the value must be either 'Restriction Digest', or 'RACE'.  The final check is for *reference_genome_assembly* in the *genomic_info* node and the ```is: GRCh38``` statement means the value must only be 'GRCh38'.  Note that is could be replaced by an enum statement containing a single enum value.

For all three of hte test, the ```scope: each``` indicates a that the test should only happen in rows where there is a value in *sample_type_category*

### Wrapping it up
If all three examples are combined into a single YAML file, it would look like this:
```YAML
conditional_rules:
  diagnosis:
    - primary_diagnosis:
        is:  NotNone
        then:
          diagnosis:
            - tumor_grade:
                scope: each
                isReq: True
            - diagnosis_id:
                scope: each
                isReq: True
  program:
    - program_short_name:
        is: BigData
        then:
          sample:
            - sample_id:
                scope: global
                is: None
  sample:
    - sample_type_category:
        is: NotNone
        then:
          sample:
            - sample_type_category:
                enum:
                  - 'DNA'
                  - 'RNA'
                scope: each
          genomic_info:
            - reference_genome_assembly:
                is: GRCh38
                scope: each
            - library_selection:
                enum:
                  - 'Restriction Digest'
                  - 'RACE'
                scope: each```