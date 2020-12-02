#!/bin/bash
#gunicorn app:app --daemon
python app/app.py & python app/worker.py