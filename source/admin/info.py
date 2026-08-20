from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from psutil import cpu_percent as CPU, virtual_memory as RAM, process_iter
from platform import system as get_platform_name

from scripts import parser
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg
import database as db


router = APIRouter()
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
            async with db.session_link() as connection:
                result = (await connection.execute(
                    db.text(query)
                )).scalars().fetchall()
                if result is None:
                    raise db.exceptions.NotFound
        elif db_type == 'fw':
            print('fw legacy call attempted')

        return JSONResponse(
            {"result": list(map(lambda t: t.to_dict(), result))},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "db returned a void", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/check_high")
async def check_high_status(
        userID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if userID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            user = await session.get(db.User, userID)
            if user is None:
                raise db.exceptions.NotFound

            firewall_entry = (await session.execute(
                db.select(db.FirewallHighEntry).where(db.FirewallHighEntry.ID == userID)
            )).scalar_one_or_none()

        return JSONResponse(
            {'result': firewall_entry is not None},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
