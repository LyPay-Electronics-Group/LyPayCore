from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from psutil import cpu_percent as CPU, virtual_memory as RAM, process_iter
from platform import system as get_platform_name

from scripts import lpsql, parser
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.MAIN_DB, lpsql.Tables.MAIN)
firewall4 = lpsql.DataBase(cfg.PATHS.FIREWALL_DB, lpsql.Tables.FIREWALL)
platform_name = get_platform_name()


@router.get("/machine")
async def get_machine_info(
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    try:
        python_processes = list()
        for running_process in process_iter():
            if running_process.name() in ("python", "python3", "python.exe") and len(running_process.cmdline()) > 0:
                python_processes.append(running_process)
        if len(python_processes) == 0:
            return parser.form_error(NameError(), "no python processes found", 404)

        r = RAM()
        return JSONResponse(
            {
                "cpu": CPU(),
                "ram_p": r.percent,
                "ram_v": (r.total - r.available) / 1073741824,
                "cpu_build": sum(list(map(lambda p: p.cpu_percent(), python_processes))) / len(python_processes),
                "ram_build_p": round(sum(list(map(lambda p: p.memory_percent(), python_processes))) / len(python_processes), 2),
                "ram_build_v": sum(list(map(lambda p: p.memory_info().rss, python_processes))) / 1073741824 / len(python_processes),
                "cpu_cores": CPU(percpu=True)
            },
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/db")
async def get_db_info(
        db_type: str = None,
        query:   str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if query is None or db_type is None or db_type not in ('main', 'fw'):
        return parser.form_error_bad_parsing()

    try:
        result = None
        if db_type == 'main':
            result = db.manual(query)
        elif db_type == 'fw':
            result = firewall4.manual(query)

        if result is None:
            raise lpsql.exceptions.EntryNotFound
        return JSONResponse(
            {"result": result},
            status_code=200
        )
    except lpsql.exceptions.EntryNotFound as e:
        return parser.form_error(e, "db returned a void", 404)
    except Exception as e:
        return parser.form_error(e)
