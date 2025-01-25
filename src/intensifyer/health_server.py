#! /usr/bin/env python3

import json
import logging
import os
import sys
from datetime import datetime

from flask import Flask

logging.getLogger("werkzeug").setLevel(logging.ERROR)

if not len(sys.argv) == 2:
    print("Usage: health_check.py [pid]")
    exit(1)

# Start healthcheck server.
health_server = Flask("health_server")


def check_pid(pid):
    """Check For the existence of a unix pid."""
    try:
        os.kill(pid, 0)
    except OSError:
        return "fail"
    else:
        return "pass"


@health_server.route("/health")
def health():
    pid = int(sys.argv[1])
    health_check = check_pid(pid)
    res = {
        "pid": pid,
        "time": datetime.now().isoformat(),
        "status": health_check,
    }
    code = 200 if health_check == "pass" else 503
    return json.dumps(res), code


health_server.run()
