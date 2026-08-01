#!/usr/bin/env python3
"""Fetch latest Whoop recovery/sleep/strain and write whoop.json.

The Whoop refresh token rotates on every use, so it is kept AES-encrypted
in the repo (.whoop_refresh.enc) with the key held as a GitHub secret.
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
API = "https://api.prod.whoop.com/developer/v2"
ENC_FILE = ".whoop_refresh.enc"
CLIENT_ID = os.environ["WHOOP_CLIENT_ID"]
CLIENT_SECRET = os.environ["WHOOP_CLIENT_SECRET"]


def openssl(extra, data):
    cmd = ["openssl", "enc"] + extra + [
        "-aes-256-cbc", "-md", "sha256", "-salt",
        "-pass", "env:WHOOP_ENC_KEY", "-base64", "-A",
    ]
    p = subprocess.run(cmd, input=data, capture_output=True)
    if p.returncode != 0:
        sys.exit("openssl failed: " + p.stderr.decode())
    return p.stdout


# Whoop's Cloudflare rejects default urllib user-agents (error 1010)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 fitday-sync"


def post_form(url, fields):
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        url, body,
        {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def api_get(path, token):
    req = urllib.request.Request(
        API + path,
        headers={"Authorization": "Bearer " + token, "User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def main():
    if not os.path.exists(ENC_FILE):
        print("no refresh token yet — run setup first; skipping")
        return

    refresh = openssl(["-d"], open(ENC_FILE, "rb").read()).decode().strip()
    tok = post_form(TOKEN_URL, {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh,
        "scope": "offline",
    })
    access = tok["access_token"]
    # persist the rotated refresh token immediately
    with open(ENC_FILE, "wb") as f:
        f.write(openssl([], tok["refresh_token"].encode()))

    out = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "recovery": None, "sleep_hours": None, "sleep_perf": None,
           "strain": None, "hrv": None, "rhr": None}

    try:
        recs = api_get("/recovery?limit=1", access).get("records", [])
        if recs:
            s = recs[0].get("score") or {}
            out["recovery"] = round(s["recovery_score"]) if s.get("recovery_score") is not None else None
            out["hrv"] = round(s["hrv_rmssd_milli"]) if s.get("hrv_rmssd_milli") is not None else None
            out["rhr"] = round(s["resting_heart_rate"]) if s.get("resting_heart_rate") is not None else None
    except Exception as e:
        print("recovery fetch failed:", e)

    try:
        recs = api_get("/activity/sleep?limit=1", access).get("records", [])
        if recs:
            s = recs[0].get("score") or {}
            st = s.get("stage_summary") or {}
            in_bed = st.get("total_in_bed_time_milli")
            awake = st.get("total_awake_time_milli") or 0
            if in_bed:
                out["sleep_hours"] = round((in_bed - awake) / 3_600_000, 1)
            if s.get("sleep_performance_percentage") is not None:
                out["sleep_perf"] = round(s["sleep_performance_percentage"])
    except Exception as e:
        print("sleep fetch failed:", e)

    try:
        recs = api_get("/cycle?limit=1", access).get("records", [])
        if recs:
            s = recs[0].get("score") or {}
            if s.get("strain") is not None:
                out["strain"] = round(s["strain"], 1)
            if s.get("kilojoule") is not None:
                out["cal_burned"] = round(s["kilojoule"] / 4.184)
            # steps aren't in the documented v2 schema, but newer WHOOP
            # hardware may expose them — pick them up if present
            for src in (s, recs[0]):
                for key in ("steps", "step_count"):
                    if isinstance(src.get(key), (int, float)):
                        out["steps"] = int(src[key])
    except Exception as e:
        print("cycle fetch failed:", e)

    with open("whoop.json", "w") as f:
        json.dump(out, f, indent=1)
    print("wrote whoop.json:", out)


if __name__ == "__main__":
    main()
