#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import warnings
import pandas as pd
import numpy as np


def import_filelist(filename):
    """
    Import text file with a list of files/directories as a list.
    :param filename: filename or reference to import, with one item per line
    :return: list of entries in the file, or empty list if file does not exist or is not specified
    """
    if filename is None or filename == "":
        filelist = []
    elif os.path.isfile(filename):
        with open(filename, 'r') as file:
            filelist = file.read().split("\n")
        filelist = [file for file in filelist if len(file) > 0]
    else:
        filelist = []
    filelist = [re.sub(r'\\', '/', item) for item in filelist]
    filelist = [re.sub(r'/$', '', item) for item in filelist]
    return filelist


def standardize_path_names(paths):
    """
    Standardize path names. Replaces home directory abbreviations with full path (e.g., ~ to /usr/<name>),
    changes backslashes to forward slashes, and removes final slash. If input is None then output is an empty list.
    :param paths: string or list of strings, paths of files/folders
    :return: string or list of strings, with elements in list standardized as path names
    """
    if paths is None:
        paths_fmt = []
    elif type(paths) == str:
        paths_fmt = [paths]
    else:
        paths_fmt = paths
    env_home = os.getenv("HOME")
    env_homedir = os.getenv("HOMEDRIVE")
    env_homepath = os.getenv("HOMEPATH")
    if env_home is not None:
        home_path = re.sub(r'\\', '/', env_home)
        paths_fmt = [re.sub(r'^~(?=/|$)', home_path, path) for path in paths_fmt]
    elif env_homedir is not None and env_homepath is not None:
        home_path = re.sub(r'\\', '/', env_homedir + env_homepath)
        paths_fmt = [re.sub(r'^%HOMEPATH%', home_path, path) for path in paths_fmt]
    paths_fmt = [re.sub(r'\\', '/', path) for path in paths_fmt]
    paths_fmt = [re.sub(r'/$', '', path) for path in paths_fmt]
    if type(paths) == str:
        paths_out = str(paths_fmt[0])
    elif type(paths) == tuple:
        paths_out = tuple(paths_fmt)
    else:
        paths_out = paths_fmt
    return paths_out


def sort_unique_items(items):
    """
    Sort and remove duplicates from list. Coerce into list (strings into list with one item, None into []).
    :param items: string or list of strings
    :return: list of strings, sorted and with only unique elements
    """
    if type(items) in [tuple, list]:
        items_out = items
    elif type(items) in (int, float, str, bool):
        items_out = [items]
    elif items is None:
        items_out = []
    else:
        items_out = list(items)
    items_out = list(set(items_out))
    items_out.sort()
    return items_out


def list_directory_files(scan):
    """
    Scan selected directory(s) for all files.
    Uses functions: standardize_path_names, sort_unique_items
    :param scan: list of directory(s) to scan
    :return: list of files/folders found in scan directory
    """
    scan_paths = standardize_path_names(scan)
    if type(scan_paths).__name__ == "str":
        scan_paths = [scan_paths]
    files_all = []
    for scan_path in scan_paths:
        for root, directories, filenames in os.walk(scan_path):
            for directory in directories:
                files_all.append(os.path.join(root, directory))
            for filename in filenames:
                files_all.append(os.path.join(root, filename))
        if os.path.isdir(scan_path) or os.path.isfile(scan_path):
            files_all.append(scan_path)
    files_all = standardize_path_names(files_all)
    files_sel = sort_unique_items(files_all)
    return files_sel


def list_possible_files(filelist, rootpath_home, rootpath_dest, skip=None, drop_nonexistent=True):
    """
    Build dataframe of all possible files/folders that could be in home or destination directories. This will define
    files/folders as if they were in either directory, and filter out anything in skip list (optional).
    Uses functions: standardize_path_names, sort_unique_items
    :param filelist: list of strings, list of all possible files using full paths
    :param rootpath_home: string, root path for home directory, used to format filelist
    :param rootpath_dest: string, root path for destination directory, used to format filelist
    :param skip: (optional) list of strings, list of files/folders to skip
    :param drop_nonexistent: boolean, whether to check for and drop files/folders that do not exist
    :return: data frame of files, with roots, endings, files as if they were in home or destination, and
             (if drop_nonexistent=True) flags for whether file/folder exists in home or destination
    """
    rootpath_home_fmt = standardize_path_names(rootpath_home)
    rootpath_dest_fmt = standardize_path_names(rootpath_dest)
    filelist_fmt = standardize_path_names(filelist)
    filelist_endings = []
    for item in filelist_fmt:
        if item.startswith(rootpath_home_fmt) and item.startswith(rootpath_dest_fmt):
            if len(rootpath_home_fmt) > len(rootpath_dest_fmt):
                ending = item[len(rootpath_home_fmt):]
            elif len(rootpath_dest_fmt) > len(rootpath_home_fmt):
                ending = item[len(rootpath_dest_fmt):]
            else:
                ending = None
        elif item.startswith(rootpath_home_fmt):
            ending = item[len(rootpath_home_fmt):]
        elif item.startswith(rootpath_dest_fmt):
            ending = item[len(rootpath_dest_fmt):]
        else:
            ending = None
        if skip is not None and ending is not None:
            skip_ending = [skip_item[len(rootpath_home_fmt):] if skip_item.startswith(rootpath_home_fmt)
                           else skip_item
                           for skip_item in skip]
            skip_flag = any([ending.startswith(skip_item) for skip_item in skip_ending])
        else:
            skip_flag = False
        if ending is not None and not skip_flag:
            filelist_endings.append(ending)
    filelist_endings = sort_unique_items(filelist_endings)
    filelist_possible_home = [rootpath_home_fmt + item for item in filelist_endings]
    filelist_possible_dest = [rootpath_dest_fmt + item for item in filelist_endings]
    if drop_nonexistent:
        flag_home_dir = []
        flag_home_file = []
        for file_home in filelist_possible_home:
            flag_home_dir.append(os.path.isdir(file_home))
            flag_home_file.append(os.path.isfile(file_home))
        flag_dest_dir = []
        flag_dest_file = []
        for file_dest in filelist_possible_dest:
            flag_dest_dir.append(os.path.isdir(file_dest))
            flag_dest_file.append(os.path.isfile(file_dest))
        flag_home = [(dir or file) for (dir, file) in zip(flag_home_dir, flag_home_file)]
        flag_dest = [(dir or file) for (dir, file) in zip(flag_dest_dir, flag_dest_file)]
        flag_any = [(home or dest) for (home, dest) in zip(flag_home, flag_dest)]
    else:
        flag_home = [None] * len(filelist_endings)
        flag_dest = [None] * len(filelist_endings)
        flag_any = [True] * len(filelist_endings)
    df_out = pd.DataFrame({
        'root_home': [rootpath_home_fmt] * len(filelist_endings),
        'root_dest': [rootpath_dest_fmt] * len(filelist_endings),
        'file': filelist_endings,
        'file_home': filelist_possible_home,
        'file_dest': filelist_possible_dest,
        'in_home': flag_home,
        'in_dest': flag_dest
    })
    if df_out.shape[0] > 0 and len(flag_any) > 0:
        df_out = df_out[flag_any]
    return df_out


def build_directory_details(filelist, rootpath, sizelimit=None, keep_hidden=True):
    """
    Build dataframe of file details, including whether directory or file, size, and time modified.
    Uses functions: standardize_path_names, sort_unique_items
    :param filelist: list of strings, files to build details for (use absolute paths)
    :param rootpath: string with root path (will be split off from file name)
    :param sizelimit: filesize limit in bytes (optional, anything larger is dropped from list)
    :param keep_hidden: boolean, whether to keep hidden files
    :return: pandas dataframe with absolute path, root, filename, directory/file flags, size, time modified
    """
    rootpath_fmt = standardize_path_names(rootpath)
    filelist_fmt = standardize_path_names(filelist)
    filelist_fmt = sort_unique_items(filelist_fmt)
    files_full = [file for file in filelist_fmt if file.startswith(rootpath_fmt)]
    files_root = [rootpath_fmt] * len(files_full)
    files_ending = [file[len(rootpath_fmt):] for file in files_full]
    if len(files_full) > 0:
        details = pd.DataFrame({
            'full': files_full,
            'root': files_root,
            'ending': files_ending,
            'dir_flag': [os.path.isdir(file) for file in files_full],
            'file_flag': [os.path.isfile(file) for file in files_full],
            'size': [os.path.getsize(file) if os.path.isfile(file) else None for file in files_full],
            'time': [os.path.getmtime(file) if os.path.isfile(file) else None for file in files_full]
        })
        is_blank = [bool(file.strip(' /\\.') == '') for file in details['ending']]
        is_file_or_dir = details['dir_flag'] | details['file_flag']
        is_temporary = [bool(re.search(r'/~', file)) for file in details['ending']]
        details = details.loc[np.logical_not(is_blank) & is_file_or_dir & np.logical_not(is_temporary), :]
        if not keep_hidden:
            is_hidden = [bool(re.search(r'/\.', file)) for file in details['ending']]
            details = details.loc[np.logical_not(is_hidden), :]
        if sizelimit is not None:
            is_file = np.logical_not(np.isnan(details['size']))
            is_big = details['size'] > sizelimit
            details = details.loc[np.logical_not(np.logical_and(is_file, is_big)), :]
    else:
        details = pd.DataFrame({
            'full': rootpath_fmt,
            'root': rootpath_fmt,
            'ending': '',
            'dir_flag': True,
            'file_flag': False,
            'size': np.nan,
            'time': np.nan
        }, index=[0])
    return details


def join_directory_details(details_home, details_dest):
    """
    Join dataframes of file details for home and destination paths.
    :param details_home: dataframe of file details for home, output from build_directory_details()
                         required fields: full, root, ending, dir_flag, file_flag, time
    :param details_dest: dataframe of file details for destination, output from build_directory_details()
                         required fields: full, root, ending, dir_flag, file_flag, time
    :return: dataframe of all files with root paths, filenames, and flags for later copying
    """
    details_join = details_home.merge(details_dest, on='ending', how='outer', suffixes=('_home', '_dest'))
    details_join = details_join.loc[list(details_join['ending'] != ""), :]
    in_dest = details_join['full_dest'].notnull()
    in_home = details_join['full_home'].notnull()
    is_dir = np.logical_or(
        np.logical_and(details_join['dir_flag_home'].notnull(), details_join['dir_flag_home']),
        np.logical_and(details_join['dir_flag_dest'].notnull(), details_join['dir_flag_dest'])
    )
    is_file = np.logical_or(
        np.logical_and(details_join['file_flag_home'].notnull(), details_join['file_flag_home']),
        np.logical_and(details_join['file_flag_dest'].notnull(), details_join['file_flag_dest'])
    )
    is_newer = np.logical_and(
        np.logical_and(details_join['time_home'].notnull(), details_join['time_dest'].notnull()),
        details_join['time_home'] > details_join['time_dest']
    )
    is_older = np.logical_and(
        np.logical_and(details_join['time_home'].notnull(), details_join['time_dest'].notnull()),
        details_join['time_home'] < details_join['time_dest']
    )
    details = pd.DataFrame({
        'root_home': details_home['root'].unique()[0],
        'root_dest': details_dest['root'].unique()[0],
        'ending': details_join['ending'],
        'in_home': in_home,
        'in_dest': in_dest,
        'is_dir': is_dir,
        'is_file': is_file,
        'is_newer': is_newer,
        'is_older': is_older
    })
    return details


def define_forced_details(paths, rootpath_home, rootpath_dest):
    """
    Build dataframe of file details for directories that will always be copied over from home to destination.
    Uses functions: standardize_path_names, sort_unique_items, list_directory_files
    :param paths: list of directories to scan, all files/subfolders here will be copied from home to destination
    :param rootpath_home: string, root path for home directory, used to format paths and file list
    :param rootpath_dest: string, root path for destination directory, used to format paths and file list
    :return: dataframe of all files with root paths, filenames, and flags for later copying
    """
    rootpath_home_fmt = standardize_path_names(rootpath_home)
    rootpath_dest_fmt = standardize_path_names(rootpath_dest)
    paths_fmt = standardize_path_names(paths)
    scan_endings = [file[len(rootpath_home_fmt):] for file in paths_fmt if file.startswith(rootpath_home_fmt)]
    filelist_home = list_directory_files([rootpath_home_fmt + ending for ending in scan_endings])
    filelist_dest = list_directory_files([rootpath_dest_fmt + ending for ending in scan_endings])
    endings_home = [file[len(rootpath_home_fmt):] for file in filelist_home if file.startswith(rootpath_home_fmt)]
    endings_dest = [file[len(rootpath_dest_fmt):] for file in filelist_dest if file.startswith(rootpath_dest_fmt)]
    endings_all = sort_unique_items(endings_home + endings_dest)
    if len(endings_all) > 0:
        file_home = [rootpath_home_fmt + ending for ending in endings_all]
        file_dest = [rootpath_dest_fmt + ending for ending in endings_all]
        is_home_dir = [os.path.isdir(file) for file in file_home]
        is_home_file = [os.path.isfile(file) for file in file_home]
        is_dest_dir = [os.path.isdir(file) for file in file_dest]
        is_dest_file = [os.path.isfile(file) for file in file_dest]
        details = pd.DataFrame({
            'root_home': rootpath_home_fmt,
            'root_dest': rootpath_dest_fmt,
            'ending': endings_all,
            'in_home': np.logical_or(is_home_dir, is_home_file),
            'in_dest': np.logical_or(is_dest_dir, is_dest_file),
            'is_dir': is_home_dir,
            'is_file': is_home_file,
            'is_newer': is_home_file,
            'is_older': [False] * len(endings_all)
        })
    else:
        details = pd.DataFrame({
            'root_home': [],
            'root_dest': [],
            'ending': [],
            'in_home': [],
            'in_dest': [],
            'is_dir': [],
            'is_file': [],
            'is_newer': [],
            'is_older': []
        })
    return details


def define_directory_commands(details, cmdtype="bash", remove_nothing=False, overwrite_anything=False):
    """
    Translate conditions into directory commands (create/delete/overwrite/ignore directory/file).
    Uses functions: standardize_path_names, sort_unique_items
    :param details: dataframe of file details with root paths, file, and flags for home/dest/dir/file/etc.
                    needs fields: root_home, root_dest, ending, is_dir, is_file, in_home, in_dest, is_newer, is_older
    :param cmdtype: string, "dos" for Windows DOS commands, "bash" for MacOS/Linux Bash commands
    :param remove_nothing: boolean, whether to avoid running any deletion commands for the destination
    :param overwrite_anything: boolean, whether to overwrite older as well as newer files in the destination
    :return: dictionary with commands ('commands') and multiple diagnostic counts ('count_*').
             'commands' is a list of commands in order: remove file, remove dir, make dir, copy file, overwrite file.
             diagnostic counts include 'count_files', 'count_folders', 'count_older', 'count_newer',
             'count_creations', 'count_deletions', and 'count_overwrites'.
    """
    list_input = standardize_path_names(details['root_home'] + details['ending'])
    list_output = standardize_path_names(details['root_dest'] + details['ending'])
    flag_mkdir = details['is_dir'] & details['in_home'] & np.logical_not(details['in_dest'])
    flag_cp = details['is_file'] & details['in_home'] & np.logical_not(details['in_dest'])
    if remove_nothing:
        flag_rmdir = [False] * details.shape[0]
        flag_rm = [False] * details.shape[0]
    else:
        flag_rmdir = details['is_dir'] & details['in_dest'] & np.logical_not(details['in_home'])
        flag_rm = details['is_file'] & details['in_dest'] & np.logical_not(details['in_home'])
    if overwrite_anything:
        flag_cpover = details['is_file'] & details['in_home'] & details['in_dest'] \
                      & details['is_newer']
    else:
        flag_cpover = details['is_file'] & details['in_home'] & details['in_dest'] \
                      & np.logical_or(details['is_newer'], details['is_older'])
    if cmdtype == "bash":
        list_input_bash = pd.Series(list_input)
        list_output_bash = pd.Series(list_output)
        cmd_rmdir = 'rm -rf "' + list_output_bash[flag_rmdir] + '"'
        cmd_mkdir = 'mkdir -p "' + list_output_bash[flag_mkdir] + '"'
        cmd_rm = 'rm -f "' + list_output_bash[flag_rm] + '"'
        cmd_cp = 'cp -R "' + list_input_bash[flag_cp] + '" "' + list_output_bash[flag_cp] + '"'
        cmd_cpover = 'cp -Rf "' + list_input_bash[flag_cpover] + '" "' + list_output_bash[flag_cpover] + '"'
    elif cmdtype == "dos":
        list_input_win = pd.Series([file.replace('/', '\\') for file in list_input])
        list_output_win = pd.Series([file.replace('/', '\\') for file in list_output])
        cmd_rmdir = 'rmdir /s /q "' + list_output_win[flag_rmdir] + '"'
        cmd_mkdir = 'mkdir "' + list_output_win[flag_mkdir] + '"'
        cmd_rm = 'del "' + list_output_win[flag_rm] + '"'
        cmd_cp = 'xcopy /h /q "' + list_input_win[flag_cp] + '" "' + list_output_win[flag_cp] + '*"'
        cmd_cpover = 'xcopy /h /q /y "' + list_input_win[flag_cpover] + '" "' + list_output_win[flag_cpover] + '"'
    else:
        cmd_rmdir, cmd_mkdir, cmd_rm, cmd_cp, cmd_cpover = ("", "", "", "", "")
    commands = list(cmd_rm) + list(cmd_rmdir) + list(cmd_mkdir) + list(cmd_cp) + list(cmd_cpover)
    count_files = details['is_file'].sum()
    count_folders = details['is_dir'].sum()
    count_older = details['is_older'].sum()
    count_newer = details['is_newer'].sum()
    count_creations = len(cmd_mkdir) + len(cmd_cp)
    count_deletions = len(cmd_rmdir) + len(cmd_rm)
    count_overwrites = len(cmd_cpover)
    return {'commands': commands,
            'count_files': count_files,
            'count_folders': count_folders,
            'count_older': count_older,
            'count_newer': count_newer,
            'count_creations': count_creations,
            'count_deletions': count_deletions,
            'count_overwrites': count_overwrites}


def check_directory_commands(commands_all):
    """
    Scan commands dictionary and results to report what they will do and generate warning messages if problems found.
    :param commands_all: dictionary of commands and diagnostic checks, output from define_directory_commands()
    :return: dictionary with two entries, 'message' with general message and summary of commands, and
             'warning_flag' indicating whether a warning was raised (True or False).
    """
    count_commands = len(commands_all['commands'])
    count_files = commands_all['count_files']
    count_folders = commands_all['count_folders']
    count_older = commands_all['count_older']
    count_newer = commands_all['count_newer']
    count_creations = commands_all['count_creations']
    count_deletions = commands_all['count_deletions']
    count_overwrites = commands_all['count_overwrites']
    notes_misc = []
    if count_files + count_folders == count_creations:
        notes_misc.append("All contents of source will be copied to destination, meaning that this is the first time "
                          "this program has been run and the destination directory does not yet exist. If that is not "
                          "true, then cancel the program now.")
    warning_flag = False
    if (count_deletions / count_files) > 0.5:
        warnings.warn("Commands will delete a large portion of files in destination. "
                      "Make sure the home and destination directories are not mixed up.",
                      Warning)
        warning_flag = True
    if count_older > count_newer:
        warnings.warn("There are more new files in destination than old files in source. "
                      "Make sure the home and destination directories are not mixed up.",
                      Warning)
        warning_flag = True
    message = [
        "Summary of commands:",
        f"{count_files} files and {count_folders} folders detected between home and destination.",
        f"{count_newer} newer files in home, {count_older} newer files in destination.",
        f"{count_commands} total commands.",
        f"{count_creations} creations, {count_deletions} deletions, {count_overwrites} overwrites.",
        ""
    ]
    if len(notes_misc) > 0:
        message = message + ["Notes:"] + notes_misc + [""]
    if warning_flag:
        message = message + ["WARNINGS FOUND. SEE OUTPUT MESSAGES.", ""]
    return {'message': message, 'warning_flag': warning_flag}


def run_directory_commands(commands, cmdtype="bash", tmpfile="~temp_backup",
                           wait_to_run=False, skip_execution=False, keep_script=False):
    """
    Execute set of directory commands.
    :param commands: list of commands for file operations
    :param cmdtype: string, "dos" for Windows DOS commands, "bash" for MacOS/Linux Bash commands
    :param tmpfile: string, name (without extension) of temporary script with commands to execute
    :param wait_to_run: boolean, whether to pause for confirmation from user before running script
    :param skip_execution: boolean, whether to skip execution of script (useful if just checking commands)
    :param keep_script: boolean, whether to keep and not delete script (useful if need to check commands)
    :return: None
    """
    if cmdtype == "bash" and commands is not None:
        cmdfile = tmpfile + ".sh"
        with open(cmdfile, "w", encoding="utf8") as file:
            for command in commands:
                file.write("%s\n" % command)
        os.system("chmod 777 " + cmdfile)
        if not skip_execution:
            if wait_to_run:
                os.system("read -rsp $'Press enter to continue...\n'")
            os.system("bash " + cmdfile)
        if not keep_script:
            os.system("rm " + cmdfile)
    elif cmdtype == "dos" and commands is not None:
        cmdfile = tmpfile + ".bat"
        with open(cmdfile, "w", encoding="utf8") as file:
            for command in commands:
                file.write("%s\n" % command)
        if not skip_execution:
            if wait_to_run:
                os.system("pause")
            os.system(cmdfile)
        if not keep_script:
            os.system("del " + cmdfile)
    else:
        print("No commands were run.")
    return None


def drop_datetime_log(outpath, contents=None):
    """
    Leave a log text file indicating the current time.
    Uses functions: standardize_path_names
    :param outpath: string, the path to drop the log file
    :param contents: (optional) string or list of strings, contents to write to file
    :return: None, but outputs log file named 'Updated-[DATETIME].txt'
    """
    outpath_fmt = standardize_path_names(outpath)
    logfile = outpath_fmt + "/" + "Updated-" + pd.datetime.now().strftime("%Y-%m-%d-%H%M%S") + ".txt"
    if contents is None:
        contents_list = [""]
    elif type(contents) == str:
        contents_list = [contents]
    else:
        contents_list = list(contents)
    logtext = [pd.datetime.now().isoformat()] + contents_list
    with open(logfile, "w", encoding="utf8") as file:
        file.write('\n'.join(logtext))

