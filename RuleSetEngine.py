import pandas as pd
import argparse
import yaml


def readYAML(yamlfile):
    with open(yamlfile) as f:
        output = yaml.load(f, Loader=yaml.FullLoader)
    return output

def loadSheetDF(loadsheetlist):
    final = {}
    for loadsheet in loadsheetlist:
        for node, filepath in loadsheet:
            temp_df = pd.read_csv(filepath, sep="\t")
            final[node] = temp_df
    return final



def main(args):
    
    #Read the config file
    configs = readYAML(args.configfile)
    rulefile = readYAML(configs['rulefile'])
    ruleset = rulefile['conditional_rules']
    
    #Create a dictionary of dataframes with the load sheets
    load_df = loadSheetDF(configs['loadsheets'])
    
    nodelist = ruleset.keys()
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose Output")

    args = parser.parse_args()

    main(args)