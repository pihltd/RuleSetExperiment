import pandas as pd
import argparse
import yaml
import bento_mdf
import operator
import sys


def readYAML(yamlfile):
    with open(yamlfile) as f:
        output = yaml.load(f, Loader=yaml.FullLoader)
    return output


def findKeyField(mdfmodel, node):
    keyprop = None
    props = mdfmodel.model.nodes[node].props
    for prop in props:
       if mdfmodel.model.props[(node, prop)].get_attr_dict()['is_key'] == 'True':
           keyprop = prop
    return keyprop
    

def loadSheetDF(loadsheetlist):
    final = {}
    for loadsheet in loadsheetlist:
        for node, filepath in loadsheet.items():
            temp_df = pd.read_csv(filepath, sep="\t")
            final[node] = temp_df
    return final

def listCheck(check_df, thenlist, checkprop, error_df, node, nodekey, thentest):
    # NEED:
    # Data frame to be checked
    # List to be checked against
    # Property to be checked.
    # error dataframe to hold the errors found
    #Step 1 - Get the DF we need to search
    #then_df = loadsheets[searchnode]
    #Step 2 - Make a dataframe of the rows with the search value
    #check_df = then_df[then_df[keyprop] == searchvalue]
    for index, row in check_df.iterrows():
        if row[checkprop] not in thenlist:
            error_df.loc[len(error_df)] = {'Severity': 'Error', 'Node': node, 'ID': row[nodekey], 'Test': thentest, 'Property': checkprop, 'Actual Value': row[checkprop], 'Required Value': thenlist}
    return error_df


def rangeCheck(check_df, rangetype, rangevalue, checkprop, error_df, node, nodekey, thentest):
    #Need:
    #Data frame to be checked
    # Range to be checked against
    # Value to be checked against
    # Property to be checked
    # Error dataframe
    rangetypes = {'lt': operator.lt, 'gt': operator.gt, 'lte': operator.le, 'gte': operator.ge}
    if rangetype not in rangetypes.keys():
        error_df.loc[len(error_df)] = {'Severity': 'Unknown Operator', 'Node': node, 'ID': nodekey, 'Test': thentest, 'Property': checkprop, 'Actual Value': checkprop, 'Required Value': None}
        return error_df
    else:
        for index, row in check_df.iterrows():
            if not rangetypes[rangetype](int(row[checkprop]), rangevalue):
                error_df.loc[len(error_df)] = {'Severity': 'Error', 'Node': node, 'ID': row[nodekey], 'Test': thentest, 'Property': checkprop, 'Actual Value': row[checkprop], 'Required Value': rangevalue}
    return error_df

def valueTypeCheck(check_df, checkdatatype, checkprop, error_df, node, nodekey, thentest):
    datatypes = {'string':str, 'integer':int, 'float':float, 'boolean': bool, 'complex': complex}
    print(f"CheckDataType: {checkdatatype}")
    if checkdatatype not in datatypes.keys():
        error_df.loc[len(error_df)] = {'Severity': 'Unknown Datatype', 'Node': node, 'ID': nodekey, 'Test': thentest, 'Property': checkprop, 'Actual Value': checkprop, 'Required Value': None}
    else:
        for index, row in check_df.iterrows():
            if not isinstance(row[checkprop, datatypes[checkdatatype]]):
                 error_df.loc[len(error_df)] = {'Severity': 'Error', 'Node': node, 'ID': row[nodekey], 'Test': thentest, 'Property': checkprop, 'Actual Value': row[checkprop], 'Required Value': checkdatatype}
    return error_df
            

def thenProcessor(thenstatement, loadsheets, mdfmodel, match_df, error_df):
    # Examine the then statement and figure out which subroutine needs to be called
    # Step 1 - Loop over each then node
    # Step 2 - Loop over the property list
    # Step 3 - Send to appropriate then type processor
    # Step 4 - Return error_df
    for thennode, thentestlist in thenstatement.items():
        keyprop = findKeyField(mdfmodel, thennode)
        #Create a compound key for the key property as seen in the if statement node
        compoundkeyprop = thennode+"."+keyprop
        for eachtest in thentestlist:
            for thenprop, thenlist in eachtest.items():
                #for thenprop, thenlist in thentestlist.items():
                for testcriteria, testlist in thenlist.items():
                    #print(f"Testcriteria: {testcriteria}")
                    # Need to determine which key property needs to be used
                    if compoundkeyprop in loadsheets[thennode].columns:
                        sendnodekey = compoundkeyprop
                    else:
                        sendnodekey = keyprop
                    if testcriteria == 'in':
                        error_df = listCheck(loadsheets[thennode], testlist, thenprop, error_df, thennode, sendnodekey, testcriteria)
                    elif testcriteria in ['lte', 'gte', 'lt', 'gt']:
                        error_df = rangeCheck(loadsheets[thennode],testcriteria, testlist, thenprop, error_df, thennode, sendnodekey, testcriteria)
                    elif testcriteria == 'value_type':
                        print("Sending for value type check")
                        error_df = valueTypeCheck(loadsheets[thennode], testlist, thenprop, error_df, thennode, sendnodekey, testcriteria)
    return error_df
      


def isCheck2(ifnode, ifprop, ifvalue, loadsheets):
    #Variant that returns a dataframe of the rows meeting the IF statement
    # Does NOT handle the THEN statment
    datatypes = {'string':str, 'int':int}
    if_df = loadsheets[ifnode]
    match_df = pd.DataFrame(columns=list(if_df.columns))
    
    if ifvalue in datatypes.keys():
        for index, row in if_df.iterrows():
            if isinstance(row[ifprop], datatypes[ifvalue]):
                match_df.loc[len(match_df)] = row
    else:
        for index, row in if_df.iterrows():
            if row[ifprop] == ifvalue:
                match_df.loc[len(match_df)] = row
    return match_df

def main(args):
    
    #Read the config file
    configs = readYAML(args.configfile)
    if args.verbose:
        print(f"Starting Configs:\n{configs}")
    rulefile = readYAML(configs['rulefile'])
    ruleset = rulefile['conditional_rules']
    if args.verbose:
        print(f"RuleSet:\n{ruleset}")
        
    # Set up the error dataframe
    columns = ['Severity', 'Node', 'ID', 'Test', 'Property', 'Actual Value', 'Required Value']
    error_df = pd.DataFrame(columns=columns)
    
    #Create a dictionary of dataframes with the load sheets
    if args.verbose:
        print(f"Load Sheets:\n{configs['loadsheets']}")
    loadsheets = loadSheetDF(configs['loadsheets'])
    if args.verbose:
        print(loadsheets)
    
    nodelist = loadsheets.keys()
    if args.verbose:
        print(f"Node List:\n{nodelist}")
        
    #Read in the MDF model
    mdfmodel = bento_mdf.MDF(*configs['mdffiles'])
        
    #And now for the fun part, checking the rules......
    checknodes = ruleset.keys()
    # Make sure that the rules we're looking at actually have a node in the model
    for checknode in checknodes:
        if checknode not in nodelist:
            print(f"ERROR: \t{checknode} not in submitted loadsheets")
        else:
            ifstatement = ruleset[checknode]['if']
            ifprop = list(ifstatement)[0]
            iftest = list(ifstatement[ifprop])[0]
            ifvalue = ifstatement[ifprop][iftest]
            thenstatement = ruleset[checknode]['then']
            
            if args.verbose:
                print(f"If Statment:\t{ifstatement}\nProperty:\t{ifprop}\nTest:\t{iftest}\nValue:\t{ifvalue}")
                
            # At this point, we need subroutines to handle each of the permitted tests
            if iftest == 'is':
                #error_df = isCheck(checknode, ifprop, ifvalue, ruleset, loadsheets,mdfmodel, error_df)
                ifmatch_df = isCheck2(checknode, ifprop, ifvalue, loadsheets)
                # error_df = thenCheck(thenstatement, loadsheets, row=, mdfmodel, error_df)
                error_df = thenProcessor(thenstatement, loadsheets, mdfmodel, ifmatch_df, error_df)
            #if iftest == 'lte':
            #    error_df = ifmatch_df = rangeCheck(checknode, ifprop, ifvalue, thenstatement, loadsheets, mdfmodel, error_df )
            
            
            #print(error_df.head())
            error_df.to_csv(configs['errorfile'], sep="\t")
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose Output")

    args = parser.parse_args()

    main(args)
    
    # Steps
    # Read if statment
    #  # Each allowed if condition will need its own subroutine to evaluate
    # Read then statements
    # Loop through dataframe indicated by if
    # For each row, check if statement
    # If if condition is triggered, get key reference for then dataframe from model
    # Search then dataframe with key value to get rows
    # Check each row for compliance with then statement
    # 
    # Relations that need to be handled
    # In/ Not In
    # Is/Is Not
    # Range lt/gt/lte/gte
    # Length  exact/min/max
    # String prefix/suffix/includes/no includes
    # Pattern/regex
    # Required True/False
    
    