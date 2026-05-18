from os import mkdir, listdir, getenv, getcwd as cwd
from os.path import exists
from platform import system as get_platform_name
from dotenv import load_dotenv as load_dotenvy

import sqlite3

from colorama import Fore as F, Style as S, init as c_init, just_fix_windows_console

from data import config as cfg
from scripts import j2, lpsql
from scripts.unix import unix
from scripts.memory import qr

c_init(autoreset=True)
if get_platform_name() == "Windows":
    just_fix_windows_console()


class Launcher:
    """
    Лаунчер LyPay

    (c) LyPay v2.3
    """

    def __init__(self):
        self.commands = {
            'exit': [''],
            'help (h)': [''],
            'settings': ['set', 'read', 'current', 'update'],
            'launch': [''],
            'shutdown': [''],
            'firewall4 (fw4)': [
                '<route> -read <ID>', '<route> -addw <ID> [...]', '<route> -removew <ID>', '<route> -addb <ID> [...]',
                '<route> -removeb <ID>', '<route> -close', '<route> -list'
            ],
            'extra': ['-store <hostID> [<ID>]', '-user <ID> <login> <password> <name>_<surname> <class> <email>'],
            '<default>': ['<sql-query>']
        }
        self.settings_array = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)

        self.last_error, self.last_success = None, None
        self.platform = get_platform_name()

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Filling config.PATHS...", end=' ')
        created_dirs = 0
        for path in cfg.PATHS.all:
            if not exists(path) and path[path.find(cwd()) + 1 + len(cwd()):].count('.') == 0:
                mkdir(path)
                if created_dirs == 0:
                    print(F.LIGHTYELLOW_EX + "missing directory(-ies) found")
                print(F.LIGHTBLACK_EX + f"> created '{path}'")
                created_dirs += 1
        if created_dirs == 0:
            print(F.LIGHTGREEN_EX + "OK")

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Checking the main database...", end=' ')
        try:
            self.db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
            self.fw = lpsql.DataBase("lypay_firewall.db", lpsql.Tables.FIREWALL)
            length = len(self.db.searchall("users", "ID"))
            print(F.LIGHTGREEN_EX + f"{length} user{'s' if length > 1 else ''} found")
        except Exception as e:
            bad_exit = True
            if "lypay_database.db" not in listdir(cfg.PATHS.DATA):
                print(F.LIGHTRED_EX + "NOT FOUND")
            else:
                print(F.LIGHTRED_EX + "UNKNOWN ERROR")
            print(F.LIGHTBLACK_EX + S.BRIGHT + f" > {e.args}")
            if bad_exit:
                input(F.LIGHTBLACK_EX + S.BRIGHT + "> press 'enter' to exit <")
                exit()

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Auction compatibility check...", end=' ')
        if self.db.searchall("stores", "ID").count("auction_transfer_route") == 0:
            self.db.insert("stores", [
                "auction_transfer_route",  # ID
                "Покупка лотов аукциона",  # name
                0,                         # hostID
                "auction_transfer_route",  # description
                False,                     # logo
                0,                         # balance
                None,                      # hostEmail
                0,                         # auctionID
                None                       # placeID
            ])
            print(F.LIGHTYELLOW_EX + S.NORMAL + "CREATED")
        else:
            print(F.LIGHTGREEN_EX + S.NORMAL + "OK")

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Reading ENVY config...", end=' ')
        found = load_dotenvy()
        if not found:
            print(F.LIGHTRED_EX + "FAILED")
            print(F.LIGHTBLACK_EX + S.BRIGHT + " > trying to find already loaded system variables...", end=' ')
            loaded_env = {
                getenv("LYPAY_HOST"),
                getenv("LYPAY_PORT"),
                getenv("LYPAY_EMAIL_MAIL"),
                getenv("LYPAY_EMAIL_HOST"),
                getenv("LYPAY_EMAIL_PORT"),
                getenv("LYPAY_EMAIL_PASSWORD"),
                getenv("LYPAY_PUBLIC_TOKENS"),
                getenv("LYPAY_ADMIN_TOKENS")
            }
            if None in loaded_env:
                print(F.LIGHTRED_EX + "FAILED",
                      "Please, check the root directory and manually configure .envy, then restart", sep='\n')
                input(F.LIGHTBLACK_EX + S.BRIGHT + "> press 'enter' to exit <")
                exit()
            else:
                print(F.LIGHTGREEN_EX + "OK")
        else:
            print(F.LIGHTGREEN_EX + "DONE")

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Last launch...", end=' ')
        unix_delta = round(unix()) - self.settings_array["last_launch"]
        time_delta_s = unix_delta % 60
        time_delta_m = unix_delta // 60 % 60
        time_delta_h = unix_delta // 60 // 60 % 24
        time_delta_d = unix_delta // 60 // 60 // 24
        time_string = f"{time_delta_d}:" if time_delta_d > 0 else ''
        time_string += f"{time_delta_h:02d}:" + f"{time_delta_m:02d}:" + f"{time_delta_s:02d} ago"
        print((F.LIGHTRED_EX if time_delta_d > 1 else F.LIGHTBLACK_EX) + time_string)

        self.update_settings("launch", True)
        # self.update_settings("launch_stamp", f"lls_{i_to_id(int(unix() * 1e6), 10)}")

    def close(self):
        self.update_settings("last_launch", int(unix()))
        self.update_settings("launch", False)
        self.update_settings("launch_stamp", None)

    def update_settings(self, key: str, value) -> int:
        """
        :param key: имя настройки для изменения
        :param value: новое значение
        :return: -1, если произошла ошибка. 0, если новое значение не совпадает по типу со старым. 1, если успешно заменено.
        """
        try:
            if type(value) is type(self.settings_array[key]) or value is None or self.settings_array[key] is None:
                self.settings_array[key] = value
                with open(cfg.PATHS.LAUNCH_SETTINGS, 'w', encoding='utf8') as f:
                    f.write(j2.to_(self.settings_array))
                return 1
            return 0
        except:
            return -1

    def error_handle(self, command: str, info: str, text: str = "") -> None:
        if len(text) > 0:
            print(S.BRIGHT + F.RED + f"[{command}]" + F.LIGHTRED_EX + f"({info}): {text}")
        else:
            print(S.BRIGHT + F.RED + f"[{command}]" + F.LIGHTRED_EX + f"({info})")
        self.last_error = command

    def success_handle(self, command: str, info: str, text: str = "") -> None:
        if len(text) > 0:
            print(S.DIM + F.GREEN + f"[{command}]" + F.LIGHTBLACK_EX + f"({info}): {text}")
        else:
            print(S.DIM + F.GREEN + f"[{command}]" + F.LIGHTBLACK_EX + f"({info})")
        self.last_success = command

    def help(self):
        print(F.LIGHTBLACK_EX + S.BRIGHT + "HELP page")
        print(F.LIGHTBLUE_EX + "Available commands:")
        for command in self.commands.keys():
            print(F.YELLOW + command, end='')
            print(': ', end='')
            print(F.GREEN + ', '.join(self.commands[command]))

    def firewall(self, *args):
        if args[0] == 'help':
            # legacy todo: help page
            pass

        elif len(args) == 2:
            route = args[0].lower()
            if route not in ('main', 'stores', 'admins', 'high'):
                self.error_handle("firewall4.argument", "KeyError", f"Bad route name: {route}")
                return

            command = args[1]
            try:
                if command == '-close':
                    self.fw.manual(f"DELETE FROM {route}")
                    self.success_handle("firewall4.close", "Success")
                elif command == '-list':
                    print('whitelist:', *self.fw.search(route, "access", 1))
                    print('blacklist:', *self.fw.search(route, "access", 0))
                else:
                    self.error_handle("firewall4.argument", "ArgumentError", f"Can't parse provided arguments {args}")
            except:
                self.error_handle("firewall4.dbIO", "IOError", "Couldn't read from the database")

        elif len(args) >= 3:
            route = args[0].lower()
            if route not in ('main', 'stores', 'admins', 'high'):
                self.error_handle("firewall4.argument", "KeyError", f"Bad route name: {route}")
                return

            command = args[1]

            try:
                ID = int(args[2])
            except ValueError:
                self.error_handle("firewall4.argument", "KeyError", f"Bad ID parse attempt: {args[2]}")
                return

            if len(args) > 3:
                comment = ' '.join(args[3:])
            else:
                comment = ''

            if command == '-addw':
                self.fw.insert(route, [
                    ID,      # ID
                    unix(),  # unix
                    True,    # access
                    comment  # comment
                ])
                self.success_handle("firewall4.add_white", "Success")
            elif command == '-removew':
                self.fw.manual(f"DELETE FROM {route} where ID = {ID} AND access = 1")
                self.success_handle("firewall4.remove_white", "Success")
            elif command == '-addb':
                self.fw.insert(route, [
                    ID,      # ID
                    unix(),  # unix
                    False,   # access
                    comment  # comment
                ])
                self.success_handle("firewall4.add_black", "Success")
            elif command == '-removeb':
                self.fw.manual(f"DELETE FROM {route} where ID = {ID} AND access = 0")
                self.success_handle("firewall4.remove_black", "Success")
            elif command == '-read':
                self.sql(f"SELECT * FROM {route}", 'fw')
                self.success_handle("firewall4.read", "Success")
            else:
                self.error_handle("firewall4.argument", "ArgumentError", f"Can't parse provided arguments {args}")

    def sql(self, arg: str, db: str = 'main'):
        try:
            if db == 'main':
                query = self.db.manual(arg)
            elif db == 'fw':
                query = self.fw.manual(arg)
            else:
                self.error_handle("sql.argument", "ArgumentError", f"Can't parse provided route: {db}")
                return

            if len(query) > 0:
                query = list(map(lambda item: list(map(str, item)), query))
                max_seps = [0] * len(query[0])
                for line in query:
                    for i in range(len(line)):
                        if len(line[i]) > max_seps[i]:
                            max_seps[i] = len(line[i])

                for line in query:
                    for i in range(len(line)):
                        print(line[i], end=' ' * (max_seps[i] + 3 - len(line[i])))
                    print()
        except sqlite3.Error as e:
            self.error_handle("search.sql", "sqlite3Error", e.__str__())
        except Exception as e:
            if self.settings_array["show_unknown_errors"]:
                self.error_handle("search.sql", "Unknown", "Unknown error: " + e.__str__())

    def extra(self, *args):
        if args[0] == 'help':
            # legacy todo: help page
            pass
        if len(args) > 1:
            if args[0] == '-store':
                try:
                    hostID = args[1]
                    last_index = len([store for store in self.db.searchall("stores", "ID") if store[0] == 'i'])
                    try:
                        storeID = args[2]
                    except IndexError:
                        storeID = f"i{str(last_index + 1).zfill(2)}"

                    self.firewall("stores", "-addw", hostID, "added via extra command")
                    self.db.insert(
                        "stores",
                        [
                            storeID,                                               # ID
                            storeID,                                               # name
                            hostID,                                                # hostID
                            f"generated by Launcher Extra at {round(unix(), 2)}",  # description
                            False,                                                 # logo
                            0,                                                     # balance
                            None,                                                  # hostEmail
                            None,                                                  # auctionID
                            None                                                   # placeID
                        ]
                    )
                    self.db.insert(
                        "shopkeepers",
                        [
                            hostID,  # userID
                            storeID  # storeID
                        ]
                    )
                    self.success_handle("extra.store", "Successfully added a store")
                except:
                    self.error_handle("extra.argument", "ArgumentError", f"Can't parse the following arguments: {args[1:]}")
            elif args[0] == '-user':
                try:
                    ID = int(args[1])
                    login = args[2]
                    password = args[3]
                    name = args[4].replace('_', ' ')
                    group = args[5]
                    email = args[6]

                    self.db.insert(
                        "users",
                        [
                            ID,        # ID
                            name,      # name
                            login,     # login
                            password,  # password
                            group,     # class
                            email,     # email
                            None,      # tag
                            0,         # balance
                            'manual',  # owner
                            unix(),    # last_online
                            False      # avatar
                        ]
                    )
                    if not exists(cfg.PATHS.QR + f"{ID}.png"):
                        qr(ID)

                    self.success_handle("extra.user", "Successfully added a user")
                except:
                    self.error_handle("extra.argument", "ArgumentError", f"Can't parse the following arguments: {args[1:]}")

            else:
                self.error_handle("extra.argument", "ArgumentError",
                                  f"There is no argument '{args[0]}' associated with 'extra'!")
        else:
            self.error_handle("extra.argument", "ArgumentError",
                              f"You have to assiciate more than 1 argument! Look here for more info: " + F.YELLOW + "help")
