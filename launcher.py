from colorama import Fore as F, Style as S, init as c_init
from source.launcher import Launcher
c_init(autoreset=True)


launcher = Launcher()

auto_restart = launcher.settings_array["auto_restart_cmd"]
if auto_restart is not None:
    raw_cmd = auto_restart.strip().split()
    cmd = list(map(lambda s: s.lower(), raw_cmd))
    print()
    print(F.LIGHTBLUE_EX + "Autorestart event", "has been triggered with following argument:")
    print(F.YELLOW + ">>> " + ' '.join(raw_cmd))
else:
    raw_cmd = ''
    cmd = list()

while True:
    if len(cmd) == 0:
        pass
    #
    elif cmd[0] == 'exit':
        break
    #
    elif cmd[0] == 'help' or cmd[0] == 'h':
        launcher.help()
    #
    elif cmd[0] == 'firewall4' or cmd[0] == 'fw4':
        try:
            launcher.firewall(*cmd[1:])
        except IndexError:
            launcher.error_handle("firewall4.argument", "ArgumentError",
                                  "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'launch':
        launcher.launch()
    #
    elif cmd[0] == 'shutdown':
        launcher.shutdown()
    #
    elif cmd[0] == 'settings':
        try:
            launcher.settings(*cmd[1:])
        except IndexError:
            launcher.error_handle("settings.argument", "ArgumentError",
                                  "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'extra':
        try:
            launcher.extra(*cmd[1:])
        except IndexError:
            launcher.error_handle("extra.argument", "ArgumentError",
                                  "You need to specify an argument for this command!")
    #
    else:
        try:
            launcher.sql(' '.join(raw_cmd))
        except:
            if launcher.settings_array["show_unknown_errors"]:
                launcher.error_handle("un_exp_0.argument", "KeyError", "Unknown command, try: " + F.YELLOW + "help")

    print()
    raw_cmd = input(S.NORMAL + F.GREEN + ">>> " + F.LIGHTGREEN_EX).strip().split()
    cmd = list(map(lambda s: s.lower(), raw_cmd))
    print(F.RESET + S.RESET_ALL, end='')

launcher.close()
