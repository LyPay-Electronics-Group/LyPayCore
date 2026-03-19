from fastapi import APIRouter
from fastapi.responses import JSONResponse

from psutil import cpu_percent as CPU, virtual_memory as RAM, process_iter
from platform import system as get_platform_name

from scripts import lpsql, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
platform_name = get_platform_name()


@router.get("/machine")
async def get_machine_info():
    try:
        python_processes = list()
        for running_process in process_iter():
            if running_process.name() == (
                    "python.exe" if platform_name == 'Windows' else
                    ("python3" if platform_name == 'Linux' else "")
            ) and len(running_process.cmdline()) > 0:  # and running_process.cmdline()[-1] == lls -- legacy part
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
                "ram_build_p": sum(list(map(lambda p: p.memory_percent(), python_processes))) / len(python_processes),
                "ram_build_v": sum(list(map(lambda p: p.memory_info().rss, python_processes))) / 1073741824 / len(python_processes),
                "cpu_cores": CPU(percpu=True)
            },
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)
