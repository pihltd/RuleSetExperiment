import pandas as pd
import numpy as np
import argparse
import bento_mdf
from crdclib import crdclib

'''
 Workflows
 Get all test nodes with rules
 For each test property in node:
  1. Collect the test condition
  2. Collect target nodes
  3. Collect target property list
For each target property:
  1. collect the scope
  2. Check if the test node and target node match
If test node and target node match:
  1. Get target dataframe
  2. if scope is each, find the matching row in the dataframe and test
  2a. If scope is global, test each row in the dataframe
if test node and target node differ:
  1. if scope is global:
  1a. get target dataframe
  1b: test each row
  2 if scope is each
  2a. Determine ID from test row to find target row
  2b. load target DF
  2c. query for target row
  2d test for target row
'''


def loadSheetDF(loadsheetlist, verbose=0):
    final = {}
    for loadsheet in loadsheetlist:
        for node, filepath in loadsheet.items():
            temp_df = pd.read_csv(filepath, sep="\t")
            final[node] = temp_df
    if verbose >= 2:
        print(final)
    return final


def populateRowErrorDF(target_test,row, target_property, target_node, error_df ):
    if 'is' in target_test:
        print('is test')
        if row[target_property] != target_test['is']:
            error_df.loc[len(error_df)] = {'Severity': 'Is error', 'Node': target_node, 'Test': 'is', 'Property': target_property, 'Actual Value': row[target_property], 'Required Value': target_test['is']}
    elif 'enum' in target_test:
        print('enum test')
        if row[target_property] not in target_test['enum']:
            error_df.loc[len(error_df)] = {'Severity': 'Enum error', 'Node': target_node, 'Test': 'enum', 'Property': target_property, 'Actual Value': row[target_property], 'Required Value': target_test['enum']}
    elif 'isReq' in target_test:
        print('isReq Test')
        if row[target_property] != target_test['isReq']:
            error_df.loc[len(error_df)] = {'Severity': 'IsReq error', 'Node': target_node, 'Test': 'isReq', 'Property': target_property, 'Actual Value': row[target_property], 'Required Value': target_test['isReq']}
    else:
        print(f"Failed match on {target_test}")
    return error_df


def checkTargetDF(test_property, test_value, target_node, target_property, target_test, loadsheets, error_df):
    test_df = loadsheets[target_node]
    #print(f"Test Dataframe:\n{test_df}")

    if target_test['scope'] == 'each':
        for index, row in test_df.iterrows():
            print(f"Checking {test_value}")
            if test_value == 'NotNone':
                print("NotNone found")
                if row[test_property] is np.nan:
                    print(f"Checking value {row[test_property]}")
                    error_df = populateRowErrorDF(target_test, row, target_property, target_node, error_df)
            elif test_value == 'None':
                if row[test_property] is not np.nan:
                    error_df = populateRowErrorDF(target_test, row, target_property, target_node, error_df)
            else:
                if row[test_property] == test_value:
                     error_df = populateRowErrorDF(target_test, row, target_property, target_node, error_df)
                
    return error_df



def main(args):
    # Parse the configs
    if args.verbose >= 1:
        print(f"Reading configuration file:\t{args.configfile}")
    configs = crdclib.readYAML(args.configfile)
    if args.verbose >= 2:
        print(f"Starting Configs:\n{configs}")

    # Read the rule set
    if args.verbose >= 1:
        print(f"Reading rule file:\t{configs['rulefile']}")
    rulefile = crdclib.readYAML(configs['rulefile'])
    ruleset = rulefile['conditional_rules']
    if args.verbose >= 2:
        print(f"RuleSet:\n{ruleset}")

    # Set up the error dataframe
    if args.verbose >= 1:
        print("Setting up error dataframe")
    columns = ['Severity', 'Node',  'Test', 'Property', 'Actual Value', 'Required Value']
    error_df = pd.DataFrame(columns=columns)

    #Create a dictionary of dataframes with the load sheets
    if args.verbose >= 1:
        print(f"Creating dataframes from load sheets:\n{configs['loadsheets']}")
    loadsheets = loadSheetDF(configs['loadsheets'], args.verbose)
    
    nodelist = loadsheets.keys()
    if args.verbose >= 1:
        print(f"Load Sheet Node List:\n{nodelist}")
        
    #Read in the MDF model
    #mdfmodel = bento_mdf.MDF(*configs['mdffiles'])
    #if args.verbose >= 1:
    #    print(f"Loaded data model {mdfmodel.handle}\t{mdfmodel.version}")


    # Evaluate the ruleset for each node
    for node in nodelist:
        # See if the node has a test
        if args.verbose >= 1:
            print(f"Chekcing {node} to see if there is a test in the rule set")
        if node in ruleset.keys():
            if args.verbose >= 1:
                print(f"Getting test list for node {node}")
            testlist = ruleset[node]
            for test in testlist:
                if args.verbose >= 2:
                    print(f"Starting test object:\t{test}")
                trigger_property = list(test.keys())[0]
                trigger_condition = test[trigger_property]['is']
                then_test_list = test[trigger_property]['then']
                if args.verbose >= 1:
                    print(f"Trigger Property:\t{trigger_property}\nTrigger Condition:\t{trigger_condition}\nThen tests:\t{then_test_list}")
    #
    #  At this point we have all the test for the trigger in then_test_list, now get the list of target nodes
    #
                target_node_list = then_test_list.keys()
                #print(f"Target nodes: {target_node_list}")
                #
                #  For each target node, get the properties and tests we need to look at.
                for target_node in target_node_list:
                    target_property_list = then_test_list[target_node]
                    for target_property_entry in target_property_list:
                        target_property = list(target_property_entry.keys())[0]
                        target_test = target_property_entry[target_property]
                        #print(f"Target node: {target_node}\tTarget property: {target_property}\tTarget test:{target_test}")
                        #
                        # Get the scope, check if trigger node and target node match
                        #
                        scope = target_test['scope']
                        if args.verbose >= 1:
                            print(f"Target Node: {target_node}\t TriggerNode: {node}")
                        if target_node == node:
                            #print(f"Nodes match with scope: {scope}")
                            error_df = checkTargetDF(trigger_property, trigger_condition, target_node, target_property, target_test, loadsheets, error_df)
                            print(f"Error Dataframe:\n{error_df}")
                        else:
                            print(f"Nodes do NOT match with scope: {scope}")



'''
                target_node = list(then_test_list.keys())[0]
                target_list = then_test_list[target_node]
                for target in target_list:
                    print(f"Target statement: {target}")
                    target_property = list(target.keys())[0]
                    target_test = list(target[target_property].keys())[0]
                    target_conditions = list(target[target_property].values())[0]
                    print(f"Target Node: {target_node}\nTarget Property: {target_property}\nTarget Test: {target_test}\nTarget Conditions: {target_conditions}")
                    if target_node == node:
                        # Get the DF for this node, and check all lines
                        test_df = loadsheets[node]
                        for index, row in test_df.iterrows():
                            if row[trigger_property] == trigger_condition:
                                # This won't work as is, need to specify which trigger condition
                                print(f"Found trigger property: {trigger_property} with trigger condiation {trigger_condition}")
                    else:
                        # Figure out the link from node to target node.
                        # Target node may have node.propert in the header, find that
                        print("We've got an else on hour hands")

'''
                
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument('-v', '--verbose', action='count', default=0, help=("Verbosity: -v main section -vv subroutine messages -vvv data returned shown"))
    args = parser.parse_args()

    main(args)