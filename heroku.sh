#!/bin/bash
#gunicorn app:app --daemon
python init.py & python app/worker.py