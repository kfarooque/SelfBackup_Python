#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config as c
import functions as f

# LOAD FILES #

list_directories = f.import_filelist(c.file_include)
list_exceptions = f.import_filelist(c.file_exclude)
list_always_copy = f.import_filelist(c.file_force)

# SCAN COMPUTER #

files_home = f.list_directory_files(list_directories)
files_dest = f.list_directory_files(c.path_destination)
files_all = f.list_possible_files(files_home + files_dest, c.path_home, c.path_destination,
                                  skip=list_exceptions + list_always_copy, drop_nonexistent=True)
details_home = f.build_directory_details(list(files_all.loc[files_all['in_home'], 'file_home']),
                                         rootpath=files_all.loc[0, 'root_home'],
                                         sizelimit=c.filesize_limit_bytes,
                                         keep_hidden=c.copy_hidden_files)
details_dest = f.build_directory_details(list(files_all.loc[files_all['in_dest'], 'file_dest']),
                                         rootpath=files_all.loc[0, 'root_dest'],
                                         sizelimit=c.filesize_limit_bytes,
                                         keep_hidden=c.copy_hidden_files)

# DEFINE ACTIONS

details_all = f.join_directory_details(details_home, details_dest)
details_forced = f.define_forced_details(list_always_copy, c.path_home, c.path_destination)
commands_all = f.define_directory_commands(details_all.append(details_forced).reset_index(), cmdtype=c.cmdtype)
commands_checks = f.check_directory_commands(commands_all)
print('\n'.join(commands_checks['message']))

# APPLY COMMANDS

if c.stop_if_warned and commands_checks['warning_flag']:
    print("Halting commands and saving execution script for review as ~check_self_backup.")
    f.run_directory_commands(commands_all['commands'], cmdtype=c.cmdtype, tmpfile="~check_self_backup",
                             wait_to_run=c.pause_for_confirmation,
                             skip_execution=True, keep_script=True)
else:
    f.run_directory_commands(commands_all['commands'], cmdtype=c.cmdtype, tmpfile="~run_self_backup",
                             wait_to_run=c.pause_for_confirmation,
                             skip_execution=c.create_executable_only, keep_script=c.create_executable_only)
    if not c.create_executable_only:
        f.drop_datetime_log(c.path_destination, contents=commands_checks['message'])
