import json
import sentry_sdk
from datetime import date
from flask import render_template, current_app, flash
from app.common.tools import wake_up
from app.backend.jobs.mock import load_init
from app.backend.jobs.arg.actc import load_ACTC
from app.backend.jobs.arg.apat import load_APAT
from app.backend.jobs.arg.aptp import load_APTP
from app.backend.jobs.arg.carx import load_CARX
from app.backend.jobs.arg.tc import load_TC
from app.backend.jobs.arg.tr import load_TR
from app.backend.jobs.uru.auvo import load_AUVO
from app.backend.jobs.uru.cur import load_CUR
from app.backend.jobs.uru.gpu import load_GPU
from app.backend.jobs.int.mss_base import load_MSS
from app.backend.jobs.int.mss_upd import upd_MSS
from app.frontend import public_bp
from app.frontend.forms import RunForm
from app.backend.jobs.update import create_career, fix_drivers, upd_CATS

orgs_list = ['all', 'mss', 'actc', 'apat', 'aptp', 'auvo',
             'carx', 'cur', 'gpu', 'tc', 'tr']


@public_bp.route('/')
def index():
    return render_template('./index.html')


@public_bp.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0


@public_bp.route('/run', methods=['GET', 'POST'])
def run_scripts():
    form = RunForm()

    if form.validate_on_submit():
        org = form.id_org.data
        year = str(form.year.data)
        if(form.manual.data):
            return load_org(org, year)

        return job(org, year)

    return render_template('./run_scripts.html', form=form)


@public_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    params = {}
    form = RunForm()

    if form.validate_on_submit():
        org = form.id_org.data
        year = str(form.year.data)
        params["urlApi"] = current_app.config["API_URL"]
        params["org"] = org
        params["year"] = year

        ret = run_job(params)
        flash('Job ID: ' + ret['job'], 'danger')

    return render_template('./dashboard.html', form=form, orgs=orgs_list)


@public_bp.route('/create/<org_id>/<year>', methods=['GET', 'POST'])
def run_create(org_id, year):
    params = {}
    params["urlApi"] = current_app.config["API_URL"]
    params["year"] = str(year)

    ans = upd_CATS(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@public_bp.route('/update/<org_id>/<upd_type>', methods=['GET', 'POST'])
def run_update(org_id, upd_type):
    params = {}
    params["org"] = org_id
    params["updType"] = upd_type
    params["urlApi"] = current_app.config["API_URL"]
    params["year"] = str(date.today().year)

    ans = run_job_upd(params)
    print(ans)
    flash('Job ID: ' + ans, 'danger')

    form = RunForm()

    # URLTO DASHBOARF
    return render_template('./dashboard.html', form=form, orgs=orgs_list)


@public_bp.route('/cats_upd/<int:year>', methods=['GET'])
def cats_upd(year):
    params = {}
    params["urlApi"] = current_app.config["API_URL"]
    params["year"] = year

    ans = upd_CATS(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@public_bp.route('/careers', methods=['GET'])
def create_careers():
    ans = create_career()

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@public_bp.route('/fix_drivers', methods=['GET'])
def fix_driver():
    ans = fix_drivers()

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@public_bp.route('/mss_upd/<year>', methods=['GET'])
def mss_upd(year):
    params = {}
    params["urlApi"] = current_app.config["API_URL"]
    params["year"] = year

    ans = upd_MSS(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


# @public_bp.route('/mss_driver_details', methods=['GET'])
# def mss_driver_details():
#     params = {}
#     params["catRCtrl"] = "motoe"
#     params["catOrigen"] = "fim-enel-motoe-world-cup"
#     params["year"] = "2020"
#     ans = mss_d.run_script_Details(params)

#     json_data = json.dumps(ans, indent=3)
#     return str(json_data)


# @public_bp.route('/actc_driver_details', methods=['GET'])
# def actc_driver_detail():
#     params = {}
#     params["catRCtrl"] = "tcpk"
#     params["catOrigen"] = "tcpk"
#     params["year"] = "2020"
#     ans = actc_d.run_script_Details(params)

#     json_data = json.dumps(ans, indent=3)
#     return str(json_data)


@public_bp.route('/init', methods=['GET'])
def init():
    params = {}
    params["urlApi"] = current_app.config["API_URL"]
    job = current_app.task_queue.enqueue_call(
        func=load_init, args=(params,), result_ttl=500, timeout=1200
    )
    job_id = job.get_id()
    print(job_id)
    sentry_sdk.capture_message(job_id)

    json_data = json.dumps({'job': job_id}, indent=3)
    return str(json_data)


@public_bp.route('/load/<org>/<year>', methods=['GET'])
def load_org(org, year):
    params = {}
    params["urlApi"] = current_app.config["API_URL"]
    params["org"] = org
    params["year"] = year

    return load_manual(params)


@public_bp.route('/load/<org>/<year>', methods=['GET'])
def upd(org, year):
    params = {}
    params["urlApi"] = current_app.config["API_URL"]
    params["org"] = org
    params["year"] = year

    return upd_manual(params)


@public_bp.route('/job/<org>/<year>', methods=['GET'])
def job(org, year):
    params = {}
    params["urlApi"] = current_app.config["API_URL"]
    params["org"] = org
    params["year"] = year

    return run_job(params)


@public_bp.route('/job/upd/<org>/<year>/<upd_type>', methods=['GET'])
def upd_job(org, year, upd_type):
    params = {}
    params["urlApi"] = current_app.config["API_URL"]
    params["org"] = org
    params["year"] = year
    params["updType"] = upd_type

    return run_job_upd(params)


@public_bp.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    job = current_app.task_queue.fetch_job(job_key)
    if(job):
        if (job.is_finished):
            json_data = json.dumps(job.result, indent=3)
            return str(json_data), 200
        elif(job.is_failed):
            return str("Error"), 400
    return "Nay!", 202


def load_manual(params):
    ret = {}
    if(params["org"] == 'all'):
        ret = load_ALL(params)
    elif(params["org"] == 'actc'):
        ret = load_ACTC(params)
    elif (params["org"] == 'apat'):
        ret = load_APAT(params)
    elif (params["org"] == 'aptp'):
        ret = load_APTP(params)
    elif (params["org"] == 'auvo'):
        ret = load_AUVO(params)
    elif (params["org"] == 'carx'):
        ret = load_CARX(params)
    elif (params["org"] == 'cur'):
        ret = load_CUR(params)
    elif (params["org"] == 'gpu'):
        ret = load_GPU(params)
    elif (params["org"] == 'mss'):
        ret = load_MSS(params)
    elif (params["org"] == 'tc'):
        ret = load_TC(params)
    elif (params["org"] == 'tr'):
        ret = load_TR(params)
    json_data = json.dumps(ret, indent=3)
    return str(json_data)


def upd_manual(params):
    ret = {}
    if(params["org"] == 'all'):
        ret = load_ALL(params, True)
    elif(params["org"] == 'actc'):
        ret = load_ACTC(params, True)
    elif (params["org"] == 'apat'):
        ret = load_APAT(params, True)
    elif (params["org"] == 'aptp'):
        ret = load_APTP(params, True)
    elif (params["org"] == 'auvo'):
        ret = load_AUVO(params, True)
    elif (params["org"] == 'carx'):
        ret = load_CARX(params, True)
    elif (params["org"] == 'cur'):
        ret = load_CUR(params, True)
    elif (params["org"] == 'gpu'):
        ret = load_GPU(params, True)
    elif (params["org"] == 'mss'):
        ret = upd_MSS(params)
    elif (params["org"] == 'tc'):
        ret = load_TC(params, True)
    elif (params["org"] == 'tr'):
        ret = load_TR(params, True)
    json_data = json.dumps(ret, indent=3)
    return str(json_data)


def run_job(params):
    job = None

    if(params["org"] == 'all'):
        job = current_app.task_queue.senqueue_call(
            func=load_ALL, args=(params,), result_ttl=86400, timeout=7200
        )
    elif(params["org"] == 'actc'):
        job = current_app.task_queue.enqueue_call(
            func=load_ACTC, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'apat'):
        job = current_app.task_queue.enqueue_call(
            func=load_APAT, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'aptp'):
        job = current_app.task_queue.enqueue_call(
            func=load_APTP, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'auvo'):
        job = current_app.task_queue.enqueue_call(
            func=load_AUVO, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'carx'):
        job = current_app.task_queue.enqueue_call(
            func=load_CARX, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'cur'):
        job = current_app.task_queue.enqueue_call(
            func=load_CUR, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'gpu'):
        job = current_app.task_queue.enqueue_call(
            func=load_GPU, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'mss'):
        job = current_app.task_queue.enqueue_call(
            func=load_MSS, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'tc'):
        job = current_app.task_queue.enqueue_call(
            func=load_TC, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'tr'):
        job = current_app.task_queue.enqueue_call(
            func=load_TR, args=(params,), result_ttl=5000, timeout=3600
        )

    job_id = job.get_id()
    print(job_id)
    sentry_sdk.capture_message(job_id)

    json_data = json.dumps({'job': job_id}, indent=3)
    return str(json_data)


def run_job_upd(params):
    job = None

    if(params["org"] == 'all'):
        job = current_app.task_queue.enqueue_call(
            func=load_ALL, args=(params, True), result_ttl=5000, timeout=3600
        )
    elif(params["org"] == 'actc'):
        job = current_app.task_queue.enqueue_call(
            func=load_ACTC, args=(params, True), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'apat'):
        job = current_app.task_queue.enqueue_call(
            func=load_APAT, args=(params, True), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'aptp'):
        job = current_app.task_queue.enqueue_call(
            func=load_APTP, args=(params, True), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'auvo'):
        job = current_app.task_queue.enqueue_call(
            func=load_AUVO, args=(params, True), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'carx'):
        job = current_app.task_queue.enqueue_call(
            func=load_CARX, args=(params, True), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'cur'):
        job = current_app.task_queue.enqueue_call(
            func=load_CUR, args=(params, True), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'gpu'):
        job = current_app.task_queue.enqueue_call(
            func=load_GPU, args=(params, True), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'mss'):
        job = current_app.task_queue.enqueue_call(
            func=upd_MSS, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'tc'):
        job = current_app.task_queue.enqueue_call(
            func=load_TC, args=(params, True), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'tr'):
        job = current_app.task_queue.enqueue_call(
            func=load_TR, args=(params, True), result_ttl=5000, timeout=3600
        )

    job_id = job.get_id()
    print(job_id)
    sentry_sdk.capture_message(job_id)

    json_data = json.dumps({'job': job_id}, indent=3)
    return str(json_data)


def load_ALL(params, upd=False):
    ret = []
    ret.append(load_ACTC(params, upd))
    wake_up()
    ret.append(load_APAT(params, upd))
    ret.append(load_APTP(params, upd))
    wake_up()
    ret.append(load_AUVO(params, upd))
    ret.append(load_CARX(params, upd))
    wake_up()
    ret.append(load_CUR(params, upd))
    ret.append(load_GPU(params, upd))
    wake_up()
    ret.append(load_TC(params, upd))
    ret.append(load_TR(params, upd))
    wake_up()
    if(upd):
        ret.append(upd_MSS(params))
    else:
        ret.append(load_MSS(params))
    return ret
