# Set Value Rules
Settings that pply before column-level vaidation
## allowed_null_values
## thouseands_separator
## set_precision

# Column Rules
## column_names
List of columns that the table must contain.  This is required
## all_columns_required
Boolean (True/False).  Default False
## no_extra_columns_allowed
Boolean.  Default False
## check_column_order
Boolean.  Default False

# Value Rules
Block Syntax
columns:
  <ColumnName>:
    <ValueRule1>
    <ValueRule2>

# Data Types and Formats
## value_type
## format_type

# Presence and Uniqueness
## required
Boolean.  Default False
## unique
Boolean.  Default False
## null
Boolean.  Default True

# Pattern and Membership
## pattern
Regex
## is_in
List of objects to match
## is_not_in
List of objects to exclude

# Exact Value Comparisons
## is
String or integer
## is_not
String or integer

# Numeric Bounds
## range
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