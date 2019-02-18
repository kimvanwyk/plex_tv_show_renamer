import os.path
import re
import shutil

import inquirer

PATTERNS = ('[\d]{1,2}?[xX]([\d]{1,2})', '[e_]p?(\d\d)', '^([\d]{1,2}) - ', 'E([\d]{1,2})',
            '\.20\d\d.[\d]{1,2}?([\d]{1,2})', '\.[\d]{1,2}?([\d]{1,2})', '^Season ([\d]{1,2})',
            'Episode ([\d]{1,2})')
    
def get_episode_details(file_name):
    res = None
    for p in PATTERNS:
        m = re.search(p, file_name)
        if m: 
            res = m.group(1)
            break
    if res:
        return ('%02d' % int(res), os.path.splitext(file_name)[1])
    return None

def get_show_name():
    return os.getcwd().split('/')[-1]

def season_rename():
    for f in os.listdir('.'):           
        shutil.move(f, 'Season %02d' % int(f[1:]))

def get_season():
    return os.getcwd().strip('/')[-2:]

def print_matches(sn):
    dirs = os.listdir('.')
    dirs.sort()
    for f in dirs:
        vals = get_episode_details(f)
        if vals:
            print(f"{f:40} -> {sn} - s{get_season()}e{vals[0]}{vals[1]}")
        else:
            print('%s not matched' % f)

def rename_files(sn):
    dirs = os.listdir('.')
    dirs.sort()
    for f in dirs:
        vals = get_episode_details(f)
        if vals:
            shutil.move(f, '%s - s%se%s%s' % (sn, get_season(), *vals))
        else:
            print('%s not matched' % f)

shows = [s for s in os.listdir('.') if all((s not in ('.', '..', 'app', '.git'), '__' not in s, os.path.isdir(s), not os.path.islink(s)))]
questions = [
    inquirer.List(
        "show",
        "Please select show",
        choices=shows,
    )
]
answers = inquirer.prompt(questions)
show = answers['show']
os.chdir(show)
seasons = [s for s in os.listdir('.') if 'Season' in s]
seasons.sort()
for s in seasons:
    os.chdir(s)
    print(f'Processing {s}')
    print_matches(show)
    questions = [
        inquirer.Confirm(
            'proceed',
            message = 'Process season?'
        )
    ]
    answers = inquirer.prompt(questions)
    if answers['proceed']:
        rename_files(show)
        print_matches(show)
    os.chdir('../')
    
