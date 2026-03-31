# tasks.py
from celery import Celery

app = Celery('tasks')
app.config_from_object('celeryconfig')


@app.task
def run_test_plan_summary_list(testPlanTool, name):
    testPlanTool.run_test_plan_summary_list([name])
