import os.path
import re
import shutil

import inquirer

PATTERNS = (
    "[\d]{1,2}\.([\d]{1,2})\.",
    "[\d]{1,2}?[xX]([\d]{1,2})",
    "[e_]p?(\d\d)",
    "^([\d]{1,2}) - ",
    "E([\d]{1,2})",
    "\.20\d\d.[\d]{1,2}?([\d]{1,2})",
    "\.[\d]{1,2}?([\d]{1,2})",
    "^[sS]eason ([\d]{1,2})",
    "[eE]pisode ([\d]{1,2})",
)


def get_episode_details(file_name):
    res = None
    for p in PATTERNS:
        m = re.search(p, file_name)
        if m:
            res = m.group(1)
            break
    if res:
        return ("%02d" % int(res), os.path.splitext(file_name)[1])
    return None


def get_show_name():
    return os.getcwd().split("/")[-1]


def season_rename():
    for f in os.listdir("."):
        shutil.move(f, "Season %02d" % int(f[1:]))


def get_season():
    return os.getcwd().strip("/")[-2:]


def get_changes(sn, debug=False):
    ''' Return a list of (original name, new name) tuples for each
    file in the current directory which would change, for the given show
    
    Print debug about changes and inabilities to match if `debug`
    '''

    dirs = os.listdir(".")
    dirs.sort()
    changes = []
    for f in dirs:
        vals = get_episode_details(f)
        if vals:
            new = f"{sn} - s{get_season()}e{vals[0]}{vals[1]}"
            if f != new:
                changes.append((f, new))
                if debug:
                    print(f"{f:40} -> {new}")
        else:
            if debug:
                print(f"{f} not matched")
    return changes


def rename_files(sn, debug=False):
    changes = get_changes(sn, debug)
    for (old, new) in changes:
        shutil.move(old, new)


shows = [
    s
    for s in os.listdir(".")
    if all(
        (
            s not in (".", "..", "app", ".git"),
            "__" not in s,
            os.path.isdir(s),
            not os.path.islink(s),
        )
    )
]
questions = [inquirer.List("show", "Please select show", choices=shows)]
answers = inquirer.prompt(questions)
show = answers["show"]
os.chdir(show)
seasons = [s for s in os.listdir(".") if "Season" in s]
seasons.sort()
for s in seasons:
    os.chdir(s)
    print(f"Processing {s}")
    changes = get_changes(show, debug=True)
    if changes:
        questions = [inquirer.Confirm("proceed", message="Process season?")]
        answers = inquirer.prompt(questions)
        if answers["proceed"]:
            rename_files(show)
            print(f"{s} processed")
    else:
        print(f"No changes to process in {s}")
    print()
    os.chdir("../")
