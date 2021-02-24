#!/bin/bash
#gunicorn app:app --daemon
# python init.py & python app/worker.py
python entrypoint.py run & python entrypoint.py run_worker