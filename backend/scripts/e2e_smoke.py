"""Manual end-to-end smoke test on a throwaway database (not part of pytest or CI).

Run from backend/ with the project venv:  python scripts/e2e_smoke.py
Needs the local Postgres from the test setup (user and password fpolink on localhost:5432) and
reaches mandiprices.co.in once. Same startup path as production: migrate, seed, create admin,
run the server, then real HTTP calls. Telegram and WhatsApp settings are overridden with fake
values so no real bot is touched. Prints PASS or FAIL per check.
"""

import json
import os
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

import sqlalchemy as sa

sys.stdout.reconfigure(encoding="utf-8")  # the Windows console defaults to cp1252

PY, BACKEND = sys.executable, os.getcwd()
DB = "fpolink_e2e"
ADMIN_URL = "postgresql+psycopg://fpolink:fpolink@localhost:5432/postgres"
PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"
PHONE = "9" + str(secrets.randbelow(10**9)).zfill(9)
PASSWORD = "E2e-" + secrets.token_urlsafe(12) + "9aZ!"
NEW_PASSWORD = "Rot-" + secrets.token_urlsafe(12) + "7bY!"
TG_SECRET = "e2e-secret"
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}", flush=True)


def call(method, path, body=None, token=None, headers=None, timeout=240):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw, status = r.read(), r.status
    except urllib.error.HTTPError as e:
        raw, status = e.read(), e.code
    except Exception as e:
        return type(e).__name__, {}
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, {}


def run(args, env, label, timeout=420):
    p = subprocess.run(args, cwd=BACKEND, env=env, capture_output=True, text=True, timeout=timeout)
    tail = (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]
    check(label, p.returncode == 0, tail[0][:90])
    return p.returncode == 0


admin = sa.create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
with admin.connect() as c:
    c.execute(sa.text(f"DROP DATABASE IF EXISTS {DB} WITH (FORCE)"))
    c.execute(sa.text(f"CREATE DATABASE {DB}"))

env = dict(os.environ)
env.update(
    DATABASE_URL=f"postgresql+psycopg://fpolink:fpolink@localhost:5432/{DB}",
    ENVIRONMENT="development",
    SENTRY_DSN="",
    RUN_SCHEDULER="false",
    TELEGRAM_ENABLED="true",
    TELEGRAM_BOT_TOKEN="000000:e2e-test-token",
    TELEGRAM_WEBHOOK_SECRET=TG_SECRET,
    TELEGRAM_AUTO_SET_WEBHOOK="false",
    WHATSAPP_ENABLED="false",
    ADMIN_PHONE=PHONE,
    ADMIN_PASSWORD=PASSWORD,
)
server = None
try:
    ok = run([PY, "-m", "alembic", "upgrade", "head"], env, "migrations apply on an empty database")
    ok = ok and run(
        [PY, "scripts/seed_statewide_foundation.py"], env, "statewide seed (38 districts)"
    )
    ok = ok and run([PY, "scripts/create_admin.py"], env, "admin bootstrap")
    if ok:
        server = subprocess.Popen(
            [PY, "-m", "uvicorn", "app.main:app", "--port", str(PORT), "--log-level", "warning"],
            cwd=BACKEND,
            env=env,
        )
        for _ in range(60):
            status, health = call("GET", "/api/health", timeout=5)
            if status == 200:
                break
            time.sleep(1)
        check(
            "server starts and /api/health is ok",
            status == 200 and health.get("db") == "ok",
            str(health),
        )

        status, tok = call("POST", "/api/auth/login", {"phone": PHONE, "password": PASSWORD})
        restricted = tok.get("access_token")
        check(
            "login forces a password change",
            status == 200 and tok.get("password_change_required") is True,
        )
        status, _ = call("GET", "/api/v1/pilot/metrics", token=restricted)
        check("restricted token cannot use admin endpoints", status in (401, 403), f"HTTP {status}")
        status, _ = call(
            "POST",
            "/api/auth/change-password",
            {"current_password": PASSWORD, "new_password": NEW_PASSWORD},
            token=restricted,
        )
        check("password rotation works", status == 200, f"HTTP {status}")
        status, tok = call("POST", "/api/auth/login", {"phone": PHONE, "password": NEW_PASSWORD})
        token = tok.get("access_token")
        check(
            "login with the new password",
            status == 200 and tok.get("password_change_required") is False,
        )
        status, me = call("GET", "/api/auth/me", token=token)
        check(
            "/api/auth/me returns the admin",
            status == 200 and me.get("role") == "admin",
            f"role={me.get('role')}",
        )

        status, out = call("GET", "/api/v1/pilot/metrics", token=None)
        check("pilot metrics need a login", status in (401, 403), f"HTTP {status}")
        status, out = call("GET", "/api/v1/pilot/metrics", token=token)
        check(
            "pilot metrics report for admin",
            status == 200 and "fpos" in out,
            f"fpos={len(out.get('fpos', []))}",
        )

        districts = ["Erode", "Coimbatore", "Salem", "Namakkal"]
        status, out = call(
            "POST",
            "/api/v1/ingestion/trigger",
            {"crops": ["tomato"], "districts": districts, "source": "agmarknet"},
            token=token,
        )
        s = out.get("summary", {})
        check(
            "live ingestion (tomato, 4 districts)",
            status == 200 and s.get("records_stored", 0) > 0,
            f"fetched={s.get('records_fetched')} stored={s.get('records_stored')} errors={s.get('errors')}",
        )

        status, out = call("GET", "/api/prices/latest?crop=tomato&district=Erode")
        rows = out.get("prices", [])
        newest = max((r["price_date"] for r in rows), default="")
        fresh = newest >= (date.today() - timedelta(days=1)).isoformat()
        check(
            "latest tomato prices are same-day",
            status == 200 and rows and fresh,
            f"{len(rows)} rows, newest {newest}",
        )

        status, out = call("GET", "/api/v1/prices/quality-summary")
        check(
            "data quality summary",
            status == 200 and out.get("total_records", 0) > 0,
            f"records={out.get('total_records')}",
        )

        market = rows[0]["market_name"] if rows else ""
        status, arb = call(
            "GET", "/api/v1/intelligence/arbitrage?crop=tomato&market=" + urllib.parse.quote(market)
        )
        ops = arb.get("opportunities", [])
        sane = 500 < (arb.get("origin_price") or 0) < 20000  # per quintal, not per kg
        moving = sum(o["distance_km"] > 0 for o in ops)
        check(
            "best-market advice (per quintal, real distances)",
            status == 200 and sane and moving > 0,
            f"origin ₹{arb.get('origin_price')}/qtl, {len(ops)} markets, {moving} with distance",
        )

        status, out = call("GET", "/api/v1/ingestion/runs", token=token)
        check(
            "ingestion run is logged",
            status == 200 and "success" in json.dumps(out),
            f"HTTP {status}",
        )

        update = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "date": 1700000000,
                "chat": {"id": 111, "type": "private"},
                "from": {"id": 111, "is_bot": False, "first_name": "E2E"},
                "text": "/start",
            },
        }
        status, _ = call(
            "POST",
            "/api/telegram/webhook",
            update,
            headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
        )
        check("Telegram webhook rejects a wrong secret", status == 403, f"HTTP {status}")
        status, _ = call(
            "POST",
            "/api/telegram/webhook",
            update,
            headers={"X-Telegram-Bot-Api-Secret-Token": TG_SECRET},
        )
        check("Telegram webhook accepts the right secret", status == 200, f"HTTP {status}")
finally:
    if server:
        server.terminate()
        server.wait(timeout=20)
    with admin.connect() as c:
        c.execute(sa.text(f"DROP DATABASE IF EXISTS {DB} WITH (FORCE)"))
    print(f"\n{sum(results)}/{len(results)} checks passed; scratch database dropped", flush=True)
