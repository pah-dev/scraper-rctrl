#!/bin/bash
#gunicorn app:app --daemon
# python init.py & python app/worker.py
gunicorn -b 0.0.0.0:5000 entrypoint:app & python entrypoint.py run_worker