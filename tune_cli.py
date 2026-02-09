#!/usr/bin/env python3
import argparse
import json
import sys
import time

from pymavlink import mavutil


DEFAULT_SYSID = 42
DEFAULT_COMPID = 191  # MAV_COMP_ID_ONBOARD_COMPUTER


def decode_param_id(raw):
    if isinstance(raw, bytes):
        return raw.split(b"\x00", 1)[0].decode("ascii", errors="ignore")
    return str(raw).split("\x00", 1)[0]


def open_link(port, baud):
    m = mavutil.mavlink_connection(port, baud=baud)
    m.wait_heartbeat(timeout=10)
    return m


def wait_param_value(m, name=None, timeout=3.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=0.5)
        if msg is None:
            continue
        pid = decode_param_id(msg.param_id)
        if name is None or pid == name:
            return msg
    return None


def fetch_all_params(m, target_sys, target_comp):
    m.mav.param_request_list_send(target_sys, target_comp)
    deadline = time.time() + 3.0
    seen = {}
    while time.time() < deadline:
        msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=0.4)
        if msg is None:
            continue
        pid = decode_param_id(msg.param_id)
        seen[pid] = msg.param_value
        deadline = time.time() + 0.8
    return seen


def cmd_list(m, target_sys, target_comp):
    seen = fetch_all_params(m, target_sys, target_comp)
    if not seen:
        print("No params received. Check sysid/compid and routing.")
        return 1
    for key in sorted(seen.keys()):
        print(f"{key}={seen[key]:.3f}")
    return 0


def cmd_get(m, target_sys, target_comp, name):
    m.mav.param_request_read_send(target_sys, target_comp, name.encode("ascii"), -1)
    msg = wait_param_value(m, name=name, timeout=3.0)
    if msg is None:
        print(f"No reply for {name}")
        return 1
    print(f"{name}={msg.param_value:.3f}")
    return 0


def cmd_set(m, target_sys, target_comp, name, value):
    m.mav.param_set_send(
        target_sys,
        target_comp,
        name.encode("ascii"),
        float(value),
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
    )
    msg = wait_param_value(m, name=name, timeout=3.0)
    if msg is None:
        print(f"No ack for {name}")
        return 1
    print(f"{name}={msg.param_value:.3f}")
    return 0


def cmd_export(m, target_sys, target_comp, out_file):
    seen = fetch_all_params(m, target_sys, target_comp)
    if not seen:
        print("No params received. Check sysid/compid and routing.")
        return 1
    payload = {
        "sysid": target_sys,
        "compid": target_comp,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "params": {k: float(seen[k]) for k in sorted(seen.keys())},
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"Exported {len(seen)} params to {out_file}")
    return 0


def cmd_import(m, target_sys, target_comp, in_file, strict):
    with open(in_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    if isinstance(payload, dict) and "params" in payload and isinstance(payload["params"], dict):
        incoming = payload["params"]
    elif isinstance(payload, dict):
        incoming = payload
    else:
        print("Invalid JSON: expected object or {\"params\":{...}}")
        return 1

    current = fetch_all_params(m, target_sys, target_comp)
    if not current:
        print("No params received. Check sysid/compid and routing.")
        return 1

    unknown = [k for k in incoming.keys() if k not in current]
    if unknown:
        print("Unknown params (skipped): " + ", ".join(sorted(unknown)))
        if strict:
            return 1

    applied = 0
    skipped = 0
    failed = 0
    for name in sorted(incoming.keys()):
        if name not in current:
            continue
        try:
            target = float(incoming[name])
        except (TypeError, ValueError):
            print(f"Invalid value for {name}: {incoming[name]!r}")
            failed += 1
            continue

        if abs(float(current[name]) - target) < 1e-4:
            skipped += 1
            continue

        rc = cmd_set(m, target_sys, target_comp, name, target)
        if rc == 0:
            applied += 1
        else:
            failed += 1

    print(f"Import done: applied={applied} skipped={skipped} failed={failed}")
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description="Set/list bridge tuning params over MAVLink")
    ap.add_argument("--port", required=True, help="Serial port, e.g. COM12 or /dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200, help="Telemetry baud")
    ap.add_argument("--sysid", type=int, default=DEFAULT_SYSID, help="Bridge MAVLink sysid")
    ap.add_argument("--compid", type=int, default=DEFAULT_COMPID, help="Bridge MAVLink compid")

    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p_get = sub.add_parser("get")
    p_get.add_argument("name")
    p_set = sub.add_parser("set")
    p_set.add_argument("name")
    p_set.add_argument("value", type=float)
    p_export = sub.add_parser("export")
    p_export.add_argument("file", help="Output JSON file")
    p_import = sub.add_parser("import")
    p_import.add_argument("file", help="Input JSON file")
    p_import.add_argument("--strict", action="store_true", help="Fail on unknown params")

    args = ap.parse_args()

    m = open_link(args.port, args.baud)
    try:
        if args.cmd == "list":
            return cmd_list(m, args.sysid, args.compid)
        if args.cmd == "get":
            return cmd_get(m, args.sysid, args.compid, args.name)
        if args.cmd == "set":
            return cmd_set(m, args.sysid, args.compid, args.name, args.value)
        if args.cmd == "export":
            return cmd_export(m, args.sysid, args.compid, args.file)
        if args.cmd == "import":
            return cmd_import(m, args.sysid, args.compid, args.file, args.strict)
        return 1
    finally:
        try:
            m.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
