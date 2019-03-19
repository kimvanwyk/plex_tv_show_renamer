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


class PlexRenamer(object):
    def __init__(self, show, debug=True):
        self.show = show
        self.debug = debug
        self.season = None
        self.season_number = None
        self.changes = None
        self.seasons = [s for s in os.listdir(".") if "Season" in s]
        self.seasons.sort()

    def get_episode_details(self, file_name):
        res = None
        for p in PATTERNS:
            m = re.search(p, file_name)
            if m:
                res = m.group(1)
                break
        if res:
            return ("%02d" % int(res), os.path.splitext(file_name)[1])
        return None

    def get_changes(self):
        """ Return a list of (original name, new name) tuples for each
        file in the current directory which would change, for the given show

        Print debug about changes and inabilities to match if `debug`
        """

        if self.season and self.season_number:
            dirs = os.listdir(".")
            dirs.sort()
            self.changes = []
            for f in dirs:
                vals = self.get_episode_details(f)
                if vals:
                    new = f"{self.show} - s{self.season_number}e{vals[0]}{vals[1]}"
                    if f != new:
                        self.changes.append((f, new))
                        if self.debug:
                            print(f"{f:40} -> {new}")
                else:
                    if self.debug:
                        print(f"{f} not matched")
            return self.changes

    def rename_files(self):
        if self.changes:
            for (old, new) in self.changes:
                shutil.move(old, new)
            if self.debug:
                print(f"{self.season} processed")
        else:
            print(f"No changes to process in {self.season}")

    def change_season(self):
        if self.season:
            # already in a season, chdir out of it
            os.chdir("../")
        if self.seasons:
            self.season = self.seasons.pop(0)
            self.season_number = self.season[-2:]
            os.chdir(self.season)
            if self.debug:
                print(f"Processing {self.season}")
            return True
        return False


def get_shows():
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
    return shows


if __name__ == "__main__":
    shows = get_shows()
    questions = [inquirer.List("show", "Please select show", choices=shows)]
    answers = inquirer.prompt(questions)
    show = answers["show"]
    os.chdir(show)
    pr = PlexRenamer(show, debug=True)
    while pr.change_season():
        changes = pr.get_changes()
        if changes:
            questions = [inquirer.Confirm("proceed", message="Process season?")]
            answers = inquirer.prompt(questions)
            if answers["proceed"]:
                pr.rename_files()
        else:
            print(f"No changes to process in {pr.season}")
        print()
