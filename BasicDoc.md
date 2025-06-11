# Set Value Rules
Settings that pply before column-level vaidation.  Not sure this applies if we're using just conditionals
## allowed_null_values
## thouseands_separator
## set_precision

# Column Rules
Same as above, the MDF really defines the column rules
## column_names
List of columns that the table must contain.  This is required
## all_columns_required
Boolean (True/False).  Default False
## no_extra_columns_allowed
Boolean.  Default False
## check_column_order
Boolean.  Default False

# Value Rules
The various value rules would be used but only in the context of conditional_rules
Block Syntax
columns:
  <ColumnName>:
    <ValueRule1>
    <ValueRule2>

## Data Types and Formats
Not sure if needed, most of this is going to be defined in the MDF
### value_type
value_type: string
Allowed values: string, integer, float, boolean, date-time, scientific?, complex?
### format_type
format_type:  (see Anjan's appendix B.  This is currently time formats)

## Presence and Uniqueness
### required
required: True
Boolean.  Default False
### unique
unique: True
Boolean.  Default False
### null
null: False
Boolean.  Default True

## Pattern and Membership
### pattern
pattern: ^[A-Z]
Must be a valid regular expression
### is_in
List of string or dictionary to match
#### Example 1: Providing a list of values
is_in:
  - 'ENG'
  - 'GER'
#### Example 2: Providing a reference to a model property
is_in:
  - property: "Country"
### is_not_in
List of objects to exclude
Same examples as above, just with "is_not_in"

## Exact Value Comparisons
### is
String or integer
### is_not
String or integer

## Numeric Bounds
### range
range:
  - lt: 100
  - gt: 50
List of lt | gt | lte | gte followed by integer

# Length Constraints
## exact_length
## min_length
## max_length

# String affixes and substrings
## prefix
## suffix
## includes
## not_include

# Precision Rules
## significant_digits
## decimal_places

# Second Order Validation
conditional_rules:
  <RuleName1>:
    if:
      column: <ColumnA>
      valuerule: <ValueRuleA>
    then:
      column: <ColumnB>
      valuerule: <ValueRuleB>


## Example Conditional Rules
conditional_rules:
  Country_Subdivision1:
    if:
      column: Country
      valuerule:
        is: 'US'
    then:
      column: Province/State
      valuerule:
        is_in:
          - property: "US_State"
Country_Subdivision2:
    if:
      column: Country
      valuerule:
        is: 'Canada'
    then:
      column: Province/State
      valuerule:
        is_in:
          - property: "Canada_Province"


Example of requiring multiple columns

diagnosis_req1:
  if:
    column: primary_diagnosis
    valuerule:
      is: 'Breast, NOS'
  then:
    columns:
      column: sex
        is: 'female'
      column: age
        required: True