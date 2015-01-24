# py-cpp-dependencies
Build the dependency tree of a C/C++ directory

##Details concerning how *scan_path* and *includes* variables work:##


###Example #1:###

scan_path = "/path/to/source/files"

includes = ["/path/to/source",]

\#include "files/toto.hpp" **may mean** /path/to/source/files/toto.hpp


###Example #2:###

scan_path = "/path/to/source"

includes = ["/path/to/source/internal","/path/to/source/external",]

\#include "toto.hpp" **may mean** /path/to/source/internal/toto.hpp **or** /path/to/source/external/toto.hpp
