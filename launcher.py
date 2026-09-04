from sys import argv


if __name__ == "__main__":
    if len(argv) == 1:
        from starter.starter import Starter

        starter = Starter("core")
        starter.launch_shell()

    else:
        from dotenv import load_dotenv as load_dotenvy

        load_dotenvy(".envy")

        if argv[1] == 'launch':
            from os import system, getenv
            from platform import system as get_platform

            if get_platform() == "Windows":
                system(
                    f"uvicorn server:app "
                    "--no-access-log "
                    f"--host {getenv('LYPAY_HOST')} "
                    f"--port {getenv('LYPAY_PORT')}"
                )

            elif get_platform() == "Linux":
                system(
                    f"uvicorn server:app "
                    "--no-access-log "
                    f"--workers $(nproc) "
                    f"--host {getenv('LYPAY_HOST')} "
                    f"--port {getenv('LYPAY_PORT')}"
                )

        elif argv[1] == 'start':
            from colorama import Fore as F, Style as S, init as c_init
            c_init(autoreset=True)

            from prompt_toolkit import PromptSession
            from prompt_toolkit.formatted_text import ANSI

            from starter.launcher import Launcher

            launcher = Launcher()
            launcher.setup()

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

            session = PromptSession()

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
                elif cmd[0] == 'firewall5' or cmd[0] == 'fw5':
                    try:
                        launcher.firewall(*cmd[1:])
                    except IndexError:
                        launcher.error_handle("firewall5.argument", "ArgumentError",
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

                prompt_text = ANSI(S.NORMAL + F.GREEN + ">>> ")
                try:
                    raw_cmd = session.prompt(prompt_text).strip().split()
                    cmd = list(map(lambda s: s.lower(), raw_cmd))
                    print(F.RESET + S.RESET_ALL, end='')
                except KeyboardInterrupt, EOFError:
                    break
