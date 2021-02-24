#!/bin/bash
#gunicorn app:app --daemon
# python init.py & python app/worker.py
gunicorn -t 150 -b 0.0.0.0:${PORT} -w 2 entrypoint:app & python entrypoint.py run_worker 
# & rqscheduler -H 0.0.0.0