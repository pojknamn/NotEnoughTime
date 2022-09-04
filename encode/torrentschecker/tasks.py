from encode.celery import app
from .logic import check_torrents, suggest_one, renderer


@app.task
def check_torr_task():
    return check_torrents()


@app.task
def suggest_task():
    return suggest_one()


@app.task
def render():
    return renderer.renderer()
