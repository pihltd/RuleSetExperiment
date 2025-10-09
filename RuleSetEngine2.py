import pandas as pd
import argparse
import bento_mdf
from crdclib import crdclib



def loadSheetDF(loadsheetlist, verbose=0):
    final = {}
    for loadsheet in loadsheetlist:
        for node, filepath in loadsheet.items():
            temp_df = pd.read_csv(filepath, sep="\t")
            final[node] = temp_df
    if verbose >= 2:
        print(final)
    return final




def main(args):
    # Parse the configs
    configs = crdclib.readYAML(args.configfile)

    # Read the rule set
    if args.verbose >= 1:
        print(f"Starting Configs:\n{configs}")
    rulefile = crdclib.readYAML(configs['rulefile'])
    ruleset = rulefile['conditional_rules']
    if args.verbose >= 2:
        print(f"RuleSet:\n{ruleset}")

    # Set up the error dataframe
    if args.verbose >= 1:
        print("Setting up error dataframe")
    columns = ['Severity', 'Node', 'ID', 'Test', 'Property', 'Actual Value', 'Required Value']
    error_df = pd.DataFrame(columns=columns)

    #Create a dictionary of dataframes with the load sheets
    if args.verbose >= 1:
        print(f"Load Sheets:\n{configs['loadsheets']}")
    loadsheets = loadSheetDF(configs['loadsheets'], args.verbose)
    
    nodelist = loadsheets.keys()
    if args.verbose >= 1:
        print(f"Node List:\n{nodelist}")
        
    #Read in the MDF model
    #mdfmodel = bento_mdf.MDF(*configs['mdffiles'])
    #if args.verbose >= 1:
    #    print(f"Loaded data model {mdfmodel.handle}\t{mdfmodel.version}")


    # Evaluate the ruleset for each node
    for node in nodelist:
        # See if the node has a test
        if node in ruleset.keys():
            testlist = ruleset[node]
            for test in testlist:
                #print(f"Starting test object:\t{test}")
                trigger_property = list(test.keys())[0]
                trigger_condition = test[trigger_property]['is']
                then_test_list = test[trigger_property]['then']
                if args.verbose >= 1:
                    print(f"Test Property:\t{trigger_property}\nTest Condition:\t{trigger_condition}\nRequired changes:\t{then_test_list}")
                '''
                There are only three possibilities here:
                1) None - As in there should not be any value in this property (np.nan?)
                2) NotNone - There should be some value in this property.  We don't care what the value is, just that there is something
                3) Anything else is considered a specifc value that must be in the property

                Where this getus ugly is figuring out where to test.  If the node and the target node are the same, test the existing line.
                If the node and the target node are different, need to find the connection field (node.property) and then search for the property value
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


                
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument('-v', '--verbose', action='count', default=0, help=("Verbosity: -v main section -vv subroutine messages -vvv data returned shown"))
    args = parser.parse_args()

    main(args)