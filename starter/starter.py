from os import getcwd
from os.path import exists
from subprocess import run, DEVNULL

from data.config import PATHS
from scripts.j2sync import to_ as j2_to, fromfile as j2_fromfile


class Starter:
    def __init__(self, session_name: str):
        self.session_name = session_name

        if not exists(PATHS.LAUNCH_SETTINGS):
            with open(PATHS.LAUNCH_SETTINGS, 'w') as f:
                f.write(j2_to({
                    "launch":                        False,
                    "starter_script":                f'cd "{getcwd()}" && source ./.venv/bin/activate && clear && python launcher.py start',
                    "auto_restart_cmd":              None,
                    "auction":                       False,
                    "user_can_register":             True,
                    "user_can_register_via_linking": False,
                    "user_can_deposit":              False,
                    "user_can_transfer":             False,
                    "user_can_use_promo":            False,
                    "store_can_register":            False,
                    "store_can_send_ad":             False,
                    "store_show_placement_data":     False,
                    "show_unknown_errors":           True,
                    "last_launch":                   0
                }))

        self.launch_cmd = j2_fromfile(PATHS.LAUNCH_SETTINGS)["starter_script"]

    def check_session(self):
        result = run(["tmux", "has-session", "-t", self.session_name], stdout=DEVNULL, stderr=DEVNULL)

        if result.returncode != 0:
            try:
                run(["tmux", "new-session", "-d", "-s", self.session_name], check=True)
            except:
                print("[!] FAILED", "session creation failed")
                exit(1)

    def launch_shell(self):
        try:
            run(["tmux", "new-session", "-A", "-s", self.session_name, self.launch_cmd], check=True)
        except:
            print("[!] FAILED", "session creation failed")
            exit(1)


__all__ = ('Starter',)
