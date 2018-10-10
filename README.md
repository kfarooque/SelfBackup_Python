# Self-Backup (Python Version)

Automated simple backup method that copies everything in one selected folder to another. More specifically, it:
(a) copies all files, folders, and subfolders from a home/source directory to a destination/backup directory,
(b) skips any files that have not been updated since the last backup, and
(c) removes any files and folders from the destination/backup directory that no longer exist in the home/source directory structure.

This works best as a frequently-run process that synchronizes a backup folder with one or more source folders. The user can specify specific folders to copy or ignore, a minimum filesize, and whether to ignore hidden files. This does not replace more complex version control like Git.

_**WARNING: THIS USES COMMANDS THAT REMOVE FILES FROM THE DESTINATION DIRECTORY WITHOUT WARNING. THE DESTINATION PATH MUST BE SEPARATE FROM ANYTHING YOU ARE BACKING UP AND CAN BE DELETED/OVERWRITTEN. MAKE SURE NOT TO MIX UP THE HOME AND DESTINATION PARAMETERS.**_

### Update Notes
|Date|Updates|
|----|-------|
|2018-10-07|Completed initial Windows/DOS and MacOS/Linux/Bash versions.

## Contents

### Scripts
* `main.py` runs the backup process.
* `config.py` (called by `main.py`) defines default parameters or pulls them from the command line.
* `functions.py` (called by `main.py`) defines all functions.

### Other Files
* `requirements.txt` requirements for running process
* `license.txt` license information
* `to_include.txt` (user-created, not in repository) lists paths of files/folders in home/source to copy to destination/backup.
* `to_exclude.txt` (user-created, not in repository) lists paths of files/folders to skip, even if they are in folders included above.
* `to_force.txt` (user-created, not in repository) lists paths of files/folders to always copy over regardless of parameters.
* `*.sh` or `*.bat` (user-created, not in repository) can be created by user to more easily run the program from the command line.

## Setup

### Input Files
1. **REQUIRED:** Create/update the file `to_include.txt` in the program's root folder, with the full paths to copy over, one per line. All files must have a common drive or path. Everything in a directory and its subdirectories will be copied (unless listed in the exclude file or over the size limit). Example content:
    ```
    ~/Documents
    ~/Projects
    ~/Media
    ```
    ```
    C:\Documents
    C:\Program Files
    ```
2. **OPTIONAL:** Create/update the file `to_exclude.txt` in the program's root folder, with the full paths of folders/files to skip when copying over, one per line. Everything in a directory and its subdirectories listed here will be skipped, even if mentioned in `to_include.txt`. Example content:
    ```
    ~/Documents/keys.txt
    ~/Media/Videos
    ```
    ```
    C:\Documents\keys.txt
    C:\Program Files\Temporary Files
    ```
3. **OPTIONAL:** Create/update the file `to_force.txt` in the program's root folder, with the full paths of folders/files to always copy over regardless of any other parameters, one per line. Everything in a directory and its subdirectories listed here will be copied over, regardless of the contents of `to_include.txt` or `to_force.txt` and whether the home or destination versions are newer or older. Example content:
    ```
    ~/Media/Videos/SpecificProject
    ~/Utilities/Backup/Installers
    ```
    ```
    C:\Program Files\Temporary Files\hidden
    C:\Utilities/Backup/Installers
    ```

### Scripts
1. **ONE-TIME ONLY:** Use `pip install` to install necessary packages: `numpy`, `pandas`. Example:
    ```bash
    python -m pip install numpy
    python -m pip install pandas
    ```
2. **AS NEEDED:** Update `config.py` to change any of the following parameters:
    * `path_home` = home/source directory (e.g., `"~"`, `"C:"`)
        * everything in `to_include.txt`/`to_exclude.txt` should begin with this path
        * alternatively, can define this parameter from the command line
    * `path_destination` = destination/backup directory (e.g., `"~/Backup"`, `"D:/Backup"`, )
        * this cannot be a subdirectory of anything listed in `to_include.txt`
        * alternatively, can define this parameter from the command line
    * `file_include` = file with directories to include (usually `"to_include.txt"`)
    * `file_exclude` = file with directories to exclude (usually `"to_exclude.txt"`)
    * `file_force` = file with directories to always copy (usually `"to_force.txt"`)
    * `filesize_limit_bytes` = filesize limit, files over this size will be ignored (e.g., 10GB would be `10 * (1024 ** 3)`)
    * `copy_hidden_files` = whether to copy hidden files with everything else
    * `prevent_file_removal` = whether to block commands that remove files/folders from destination
    * `overwrite_older_and_newer` = whether to overwrite older and newer (instead of just older) files in destination
    * `stop_if_warned` = whether to stop process if it detects possible mistakes
    * `pause_for_confirmation` = whether to pause for confirmation before running commands
    * `create_executable_only` = whether to create an executable instead of running commands
    * Other recommendations when defining files and directory names:
        * use only forward-slashes (`/`) instead of backslashes (`\\`) - both will work, but `\\`s can cause escape errors sometimes, and either type is converted to whatever is needed for the operating system
        * do not end directories with a final slash (`/` or `\\`) - this will probably still work but the program is less likely to encounter errors if you do not end parameter definitions with a slash
3. **OPTIONAL** Create/update a `*.sh` (MacOS/Linux) or `*.bat` (Windows) file to more easily run the python script from the command line (see **Operation > Run from Command Line** section for how to define it).

## Operation

### Run from Python Interpreter
1. Update `config.py` with parameters for directories and files (see **Setup > Scripts** section above).
    * _**Be careful about how you define `path_destination`! Anything in that directory can be deleted or overwritten.**_
2. Run `main.py` from the Python interpreter.
3. Check your output in the destination directory. There should be a text file dropped there with the date, time, and summary of this backup if it ran successfully.

### Run from Command Line
1. If necessary, update `config.py` with default parameters for directories and files (see **Setup > Scripts** section above).
    * _**Be careful about how you define `path_destination`! Anything in that directory can be deleted or overwritten.**_
2. Run `main.py` from the command line using the following syntax:
    ```sh
    python main.py <HOME> <DESTINATION>
    ```
    * `<HOME>` is the home path, enclosed in ""s.
    * `<DESTINATION>` is the destination/backup path, enclosed in ""s.
        * _**Be careful about how you define this! Anything in this directory can be deleted or overwritten.**_
    * If neither parameter is defined, then the program will use the values defined in `config.py`.
    * Do not use backslashes before quotation marks (e.g., `"C:\"`), since the backslash will escape the quotation mark. Instead, define without the final backslash (e.g., `"C:"`), or use a forward slash (e.g., `"C:/"`).
3. If you will be running this regularly, then create a `*.sh` (MacOS/Linux) or `*.bat` (Windows) file with the command(s) from Step 2.

Examples in MacOS or Linux:
```bash
python main.py
python main.py "~" "~/Backup"
```

Examples in Windows:
```bash
python main.py
python main.py "C:" "D:\Backup"
```
