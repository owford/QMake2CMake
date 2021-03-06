from .qmake_to_cmake import QMakeToCMake
from .cmake_writer import CMakeFileAlreadyExistsError
from .config_visitor import ConfigVisitor
import os
import json

def get_pro_file_from_path(dir):

    if os.path.isfile(dir) and (dir.endswith(".pro") or dir.endswith(".pri")):
        return dir
    if os.path.isdir(dir) is False:
        raise ValueError('%s is not a directory'%(dir))

    candidates = []
    for file in os.listdir(dir):
        if file.endswith(".pro"):
            candidates.append(os.path.join(dir, file))

    if len(candidates) is 0:
        raise ValueError('%s does not contains .pro file' % (dir))

    if len(candidates) > 1:
        raise ValueError('%s does contains severals .pro file %s' % (dir, ' '.join(candidates)))

    return candidates[0]


import argparse
import webbrowser


def dict_from_json_file(json_file):
    if json_file is None:
        return None

    with open(json_file) as json_data:
        return  json.load(json_data)



def TryConvert(path, dry_run, show, config,show_method = webbrowser.open_new_tab):
    converter = QMakeToCMake()

    dico = dict_from_json_file(config)
    visitor = None
    if dico is not None:
        visitor = ConfigVisitor(dico)

    converter.register_config_visitor(visitor)
    pro_file = get_pro_file_from_path(path)
    if dry_run is True:
        converter.convertToStdOut(pro_file)
    else:
        try:
            converter.convert(pro_file)
            if show:
                show_method(pro_file)
                show_method(converter.get_cmakefile())
        except CMakeFileAlreadyExistsError as e:
            print(e.value)

def get_all_pro_files_from_dir_tree(dir):
    pro_files = []
    for dirpath, subdirs, files in os.walk(dir):
        for x in files:
            if x.endswith(".pro"):
                pro_files.append(os.path.join(dirpath, x))
                break
    return pro_files

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="directory or file")

    parser.add_argument('-n', '--dry-run', help="print cmakelist.txt on the console",
                        action="store_true")

    parser.add_argument('-r', '--recursive', help="walk all subdirectories",
                        action="store_true")

    parser.add_argument('-s', '--show', help="show result file(s)",
                        action="store_true")

    parser.add_argument('-c', '--config', default=None,
                        help='json file defining dictionnary between CONFIG values in .pro file and cmake function')
    return parser




def main(recursive,dry_run,show,config,path,wait_for_key_pressed_method,show_file_method):

    if recursive is False:
        TryConvert(path, dry_run, show, config )
    else:
        print("------- recursive mode --------")

        pro_files = get_all_pro_files_from_dir_tree(path)

        for pro_file in pro_files:
            print("start %s conversion\n"%(pro_file))
            TryConvert(pro_file, dry_run, show,config,show_file_method)
            if show is True:
                wait_for_key_pressed_method("press enter to continue")
import sys

def entry_point():
    # python 2/3 compat
    input_method = None
    try:
        input_method = raw_input
    except NameError:
        input_method = input

    parser = create_parser()
    args = parser.parse_args()
    main(recursive=args.recursive,
         dry_run=args.dry_run,
         show=args.show,
         config=args.config,
         path=args.path,
         wait_for_key_pressed_method=input_method,
         show_file_method=webbrowser.open_new_tab)
    sys.exit(0)


if __name__ == '__main__':
    entry_point()
