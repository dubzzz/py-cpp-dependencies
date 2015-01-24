from os import listdir, path
import json
import re

class Logger:
    def info(self, msg):
        print(msg)

def scan_directory(scan_path, allowed_extensions):
    r"""
    scan_path               path to scan
    allowed_extensions      extensions to consider
    """
    
    files = list()
    for f in listdir(scan_path):
        full_path = path.join(scan_path, f)
        if path.isdir(full_path):
            subfiles = scan_directory(full_path, allowed_extensions)
            for sf in subfiles:
                files.append(sf)
        else:
            correct_extension = False
            for ext in allowed_extensions:
                if f.endswith(ext):
                    correct_extension = True
                    break
            if correct_extension:
                files.append(full_path)
    return files

def build_dependency_tree(scan_path, includes, output):
    r"""
    scan_path               path to scan
    includes                directories to find includes
    output                  filename of the output
    """

    logger = Logger()

    # Get files to analyse
    logger.info("List of files to analyse:")
    allowed_extensions = [".c", ".cpp", ".c++", ".cxx", ".h", ".hpp", ".h++", ".hxx", ".r",]
    files = scan_directory(scan_path, allowed_extensions)
    del allowed_extensions
    logger.info("> %d potential source files" % (len(files),))
    
    # Filter files on blacklist criteria
    include_files = list()
    dependency_tree = list()
    blacklist_criteria = [re.compile(r'sources\/others'),]
    for f in files:
        blacklisted = False
        for criteria in blacklist_criteria:
            if criteria.search(f.replace('\\', '/')):
                blacklisted = True
                break
        if not blacklisted:
            include_files.append(f)
            dependency_tree.append({"file": f[len(scan_path):].replace('\\', '/'), "includes": list(), "used_by": list(),})
    del blacklist_criteria
    del files
    logger.info("> %d non-blacklisted source files" % (len(dependency_tree),))

    # Read source files for includes
    logger.info("Read and parse all files")
    include_regex = re.compile(r'#include\s+([\"<"]{1})([^"^>]+)([\">"]{1})')
    for source in include_files:
        with open(source, 'r') as f:
            source_id = include_files.index(path.join(scan_path, source.replace('/', path.sep)))
            for line in f:
                # Is the line corresponding to an include?
                m = include_regex.search(line)
                if m and (m.group(1) == m.group(3) or (m.group(1) == '<' and m.group(3) == '>')):
                    include_name = m.group(2)
                    # What is the related file?
                    for include in includes:
                        # Build the path corresponding to <include>
                        include_path = include
                        for subdir in include_name.split('/'):
                            include_path = path.join(include_path, subdir)

                        # Known file?
                        if include_path in include_files:
                            include_id = include_files.index(include_path)
                            dependency_tree[source_id]["includes"].append(include_id)
                            dependency_tree[include_id]["used_by"].append(source_id)
                            break
        logger.info("> %d include(s)\tfor %s" % (len(dependency_tree[source_id]["includes"]),source,))

    with open(output, 'w') as f:
        f.write(json.dumps(dependency_tree))

def load_dependency_tree(output):
    with open(output, 'r') as f:
        return json.loads(f.read())
    return list()

def who_is_using(scan_path, output, filename):
    if not filename.startswith(scan_path):
        raise Exception("Filename does not correspond to the scan path")

    dependency_tree = load_dependency_tree(output)
    include_files = list()
    for dep in dependency_tree:
        include_files.append(path.join(scan_path, dep["file"][1:].replace('/', path.sep)))

    if not filename in include_files:
        raise Exception("Filename has not been scanned")

    using_this_file = [filename,]
    to_analyse = [include_files.index(filename),]
    while len(to_analyse) > 0:
        for f_id in dependency_tree[to_analyse[0]]["used_by"]:
            if not include_files[f_id] in using_this_file:
                using_this_file.append(include_files[f_id])
                to_analyse.append(f_id)
        dependency_tree[to_analyse[0]]["used_by"] = list()
        del to_analyse[0]

    return using_this_file

if __name__ =='__main__':
    scan_path = "/path/to/source/files"
    includes = ["/path/to/source",] # include "files/toto" can mean /path/to/source/files/toto
    output = "/path/to/output.json"
    test_path = "/path/to/source/files/foo.hpp"

    build_dependency_tree(scan_path, includes, output)
    print(who_is_using(scan_path, output, test_path))

