import bento_mdf
import argparse
from crdclib import crdclib




def main(args):
    configs = crdclib.readYAML(args.configfile)

    mdfmodel = bento_mdf.MDF(*configs['mdffiles'])

    rels = mdfmodel.model.edges

    trigger_node = 'sample'
    target_node = 'genomic_info'
    trigger_rels = []
    target_rels = []
    for rel in rels:
        # rel structure:  rel[0]: handle, rel[1]: source, rel[2]: destination
        if trigger_node in rel:
            trigger_rels.append(rel)
        elif target_node in rel:
            target_rels.append(rel)
    print(f"Trigger relations:\n{trigger_rels}")
    print(f"Target relations:\n{target_rels}")

    # Is there a direct link?
    links = []
    for target_rel in target_rels:
        if trigger_node in target_rel:
            links.append(target_rel)

    print(f"Direct Trigger to Target relation: {links}")

    #No direct connections found
    if len(links) == 0:
        for rel in trigger_rels:
                for target_rel in target_rels:
                    if rel[1] in target_rel:
                        links.append(target_rel)
                    elif rel[2] in target_rel:
                        links.append(target_rel)
    print(f"Broad search: {links}")

    # At this point we need to consider multiple hops.
            



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument('-v', '--verbose', action='count', default=0, help=("Verbosity: -v main section -vv subroutine messages -vvv data returned shown"))
    args = parser.parse_args()

    main(args)
