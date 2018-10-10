#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import os

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
prevent_file_removal = False
overwrite_older_and_newer = False
stop_if_warned = True
pause_for_confirmation = True
create_executable_only = False

# AUTOMATIC INPUTS #

# replace defaults with command-line parameters if given
if len(sys.argv) > 0:
    if sys.argv[0] in ('main.py', 'config.py'):
        if len(sys.argv) > 1:
            path_home = sys.argv[1]
        if len(sys.argv) > 2:
            path_destination = sys.argv[2]

# reset parameters that only work with command line
if len(sys.argv) == 0:
    pause_for_confirmation = False
elif sys.argv[0] not in ('main.py', 'config.py'):
    pause_for_confirmation = False

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
    '\n', f"Including files in {file_include}.",
    f"Excluding files in {file_exclude}." if os.path.isfile(file_exclude) else "",
    f"Always copying files in {file_force}." if os.path.isfile(file_force) else "",
    '\n', f"Ignoring files over {filesize_limit_bytes} bytes." if filesize_limit_bytes is not None else "",
    f"Keeping hidden files." if copy_hidden_files else f"Ignoring hidden files.",
    f"Removing no files from destination." if prevent_file_removal else f"May remove files from destination.",
    f"Copying any different files." if overwrite_older_and_newer else f"Copying only newer files.",
    '\n', f"Will halt process if warnings detected." if stop_if_warned else "",
    f"Will pause for confirmation before running final step." if pause_for_confirmation else "",
    f"Will only create but not run executable." if create_executable_only else "",
    '\n', f"Using {cmdtype}-style commands for deleting, copying, and overwriting.",
    '\n'
)
