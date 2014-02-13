#!/usr/bin/python

import os
import sys
import fnmatch
import subprocess

def find_path(candidates, target):
    for candidate in candidates:
        candidate = candidate.rstrip('\r\n')

        if os.path.exists(candidate):
            for root, dirnames, filenames in os.walk(candidate):
                for filename in fnmatch.filter(filenames, target):
                    return os.path.join(root)


    return ""


# Check the system platform first
platform = sys.platform
print "This is a " + platform + " system"

# Open the configure file and start parsing
config = open('.cfg', 'r')
success = True

for line in config:
    path = line.split(' ')

    if path[0] == "MATLAB_PATH":
        print "Searching for Matlab path ..."
        matlab_path = find_path(path[1].split(','), 'matlab')
        if matlab_path == "":
            print "Cannot find Matlab. Please add the path to .cfg"
            success = False
            break
        print "Done"

    elif path[0] == "HEADER_PATH":
        print "Searching for zmq.h ..."
        header_path = find_path(path[1].split(','), 'zmq.h')
        if header_path == "":
            print "Cannot find zmq.h. Please add the path to .cfg"
            success = False
            break
        print "Done"

    elif path[0] == "LIB_PATH":
        # Dynamic library has different names on different platforms
        if platform == 'darwin':
            print "Searching for libzmq.dylib ..."
            lib_path = find_path(path[1].split(','), 'libzmq.dylib')
        elif platform == 'linux2':
            print "Searching for libzmq.so ..."
            lib_path = find_path(path[1].split(','), 'libzmq.so')
        elif platform == 'win32':
            print "Searching for libzmq.dll ..."
            lib_path = find_path(path[1].split(','), 'libzmq.dll')

        if lib_path == "":
            print "Cannot find libzmq. Please add the path to .cfg"
            success = False
            break
        print "Done"

config.close()

if success == False:
    print "Building failed"

# Get the extension
if platform == 'win32':
    mexext = "\\mexext"
else:
    mexext = "/mexext"
check_extension = subprocess.Popen(matlab_path + mexext, stdout = subprocess.PIPE)
extension = check_extension.stdout.readline().rstrip('\r\n')

# Build the mex file
if platform == 'win32':
    mex = "\\mex"
else:
    mex = "/mex"
make_cmd = matlab_path + mex + " -O -I" + header_path + " -L" + lib_path + " -lzmq messenger.c"
os.system(make_cmd)

# Move to the ../matlab/ directory
if platform == 'win32':
    move_cmd = "mv messenger." + extension + " ..\\matlab\\"
else:
    move_cmd = "mv messenger." + extension + " ../matlab/"

os.system(move_cmd)

print "Building succeeded!"