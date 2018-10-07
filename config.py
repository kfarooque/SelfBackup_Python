#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re

# USER INPUTS #

# default files and paths
path_home = None
path_destination = None
file_include = "to_include.txt"
file_exclude = "to_exclude.txt"
file_force = "to_force.txt"

# operational parameters
filesize_limit_bytes = 10 * (1024 ** 3)
copy_hidden_files = True
stop_if_warned = True
pause_for_confirmation = True
create_executable_only = False

# AUTO INPUTS #

# replace defaults with command-line parameters if given
if len(sys.argv) > 0:
    if sys.argv[0] in ('main.py', 'config.py'):
        if len(sys.argv) > 1:
            path_home = sys.argv[1]
        if len(sys.argv) > 2:
            path_destination = sys.argv[2]

# detect system commands (dos or bash)
if re.search(r'^win', sys.platform) is not None:
    cmdtype = "dos"
elif re.search(r'linux|unix|darwin|posix|osx|macos', sys.platform) is not None:
    cmdtype = "bash"
else:
    cmdtype = "unknown"

# REPORTS #

print(
    '\n', f"Backing up files from {path_home} to {path_destination}",
    '\n', f"Including files in {file_include}, excluding files in {file_exclude}, always copying files in {file_force}.",
    '\n', f"Ignoring files over {filesize_limit_bytes} bytes." if filesize_limit_bytes is not None else "",
    '\n', f"Keeping hidden files." if copy_hidden_files else f"Ignoring hidden files.",
    '\n', f"Using {cmdtype}-style commands for deleting, copying, and overwriting.",
    '\n'
)
