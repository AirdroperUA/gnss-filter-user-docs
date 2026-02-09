# Tools

## `tune_cli.py`

`tune_cli.py` is a MAVLink CLI for reading and writing filter tuning parameters from a PC.

It talks to the filter (`SYSID=42`, `COMPID=191` by default) over a MAVLink serial link.

### Requirements

- Python 3.9+
- `pymavlink`

Install:

```bash
python -m pip install pymavlink
```

### Basic Usage

From repository root:

```bash
python tools/tune_cli.py --port COM12 --baud 115200 list
```

Commands:

- `list` - read all exposed tune params.
- `get <name>` - read one param.
- `set <name> <value>` - set one param.
- `export <file.json>` - save all params to JSON.
- `import <file.json>` - apply values from JSON.

Examples:

```bash
python tools/tune_cli.py --port COM12 --baud 115200 get BLEND_MS
python tools/tune_cli.py --port COM12 --baud 115200 set RJ_BASE_M 180
python tools/tune_cli.py --port COM12 --baud 115200 export tune_baseline.json
python tools/tune_cli.py --port COM12 --baud 115200 import tune_baseline.json
python tools/tune_cli.py --port COM12 --baud 115200 import tune_baseline.json --strict
```

### JSON Format

`export` writes:

```json
{
  "sysid": 42,
  "compid": 191,
  "timestamp_utc": "2026-01-28T14:12:00Z",
  "params": {
    "BLEND_MS": 10000.0
  }
}
```

`import` accepts either:

- wrapper object with `"params"` key, or
- plain object `{ "PARAM_NAME": value, ... }`.

### Notes

- Use the FC telemetry link that carries filter MAVLink traffic.
- If `list` returns no params, check wiring, serial baud/protocol, and `--sysid/--compid`.

## `updater/`

`updater/` contains secure-update tooling:

- `gen_keys.py`
- `sign_release.py`
- `update_client.py`
- `sign_phaseb.py`
- `export_boot_pubkey.py`

See `tools/updater/README.md`.
