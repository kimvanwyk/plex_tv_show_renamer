import os.path
import re
import shutil

import inquirer

PATTERNS = (
    r"E([\d]{1,2})_",
    r"[\d]{1,2}\.([\d]{1,2})\.",
    r"[\d]{1,2}?[xX]([\d]{1,2})",
    r"[e_]p?(\d\d)",
    r"^([\d]{1,2}) - ",
    r"E([\d]{1,2})",
    r"\.20\d\d.[\d]{1,2}?([\d]{1,2})",
    r"\.[\d]{1,2}?([\d]{1,2})",
    r"^[sS]eason ([\d]{1,2})",
    r"[eE]pisode ([\d]{1,2})",
    r"[sS]eries [\d]{1,2}, ([\d]{1,2})",
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
        """Return a list of (original name, new name) tuples for each
        file in the current directory which would change, for the given show

        Print debug about changes and inabilities to match if `debug`
        """

        if self.season and self.season_number:
            dirs = os.listdir(".")
            dirs.sort()
            self.changes = []
            existing = []
            for f in dirs:
                vals = self.get_episode_details(f)
                if vals:
                    new = f"{self.show} - s{self.season_number}e{vals[0]}{vals[1]}"
                    if f != new:
                        self.changes.append((f, new))
                    else:
                        existing.append(f)
                else:
                    if self.debug:
                        print(f"{f} not matched")
            if self.changes and self.debug:
                if existing:
                    print("Existing episodes:")
                    print("\n".join(f for f in existing))

                print("Proposed changes:")
                for f, new in self.changes:
                    print(f"{f:40} -> {new}")

            return self.changes

    def rename_files(self):
        if self.changes:
            for old, new in self.changes:
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
                print(f"Processing {self.show} - {self.season}")
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
    questions = [
        inquirer.List(
            "show", "Please select show", choices=["Process all shows"] + shows
        )
    ]
    answers = inquirer.prompt(questions)
    if answers["show"] != "Process all shows":
        shows = [answers["show"]]
    for show in shows:
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
        os.chdir("../")
