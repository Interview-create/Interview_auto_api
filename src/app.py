import asyncio
import os
import subprocess

from core.TestPlanTool import TestPlanTool
from flask import Flask, render_template_string, send_from_directory, request
from flask_socketio import SocketIO, emit
from tasks import run_test_plan_summary_list
from gevent import spawn
from gevent.pywsgi import WSGIServer
from utils import config
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app)

# 指定要瀏覽的目錄
base_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')


@app.route('/')
async def home():
    file_list = os.listdir(base_directory)
    links = []

    for item in file_list:
        item_path = os.path.join(base_directory, item)
        if os.path.isfile(item_path):
            links.append(f'<a href="/file/{item}">{item}</a>')
        elif os.path.isdir(item_path):
            links.append(f'<a href="/folder/{item}">{item}</a>')

    links_html = '<br>'.join(links)
    return render_template_string(f'<div>{links_html}</div>')


@app.route('/file/<path:filename>')
async def serve_file(filename):
    return send_from_directory(base_directory, filename)


@app.route('/folder/<path:folderName>')
async def serve_folder(folderName):
    folder_path = os.path.join(base_directory, folderName)
    file_list = os.listdir(folder_path)
    links = []

    for item in file_list:
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            links.append(f'<a href="/file/{folderName}/{item}">{item}</a>')
        elif os.path.isdir(item_path):
            links.append(f'<a href="/folder/{folderName}/{item}">{item}</a>')

    links_html = '<br>'.join(links)
    return render_template_string(f'<div>{links_html}</div>')


def run_test_plan_in_background(testPlanTool, name):
    testPlanTool.run_test_plan_summary_list([name])


@app.route('/run')
async def run():
    name = request.args.get('name')
    testPlanTool = TestPlanTool()
    # await testPlanTool.run_test_plan_summary_list([name])

    # 使用 Celery 任务在后台运行 run_test_plan_summary_list 方法
    run_test_plan_summary_list.delay(testPlanTool, name)

    # 使用 gevent.spawn 在后台运行 run_test_plan_summary_list 方法
    # spawn(run_test_plan_in_background, testPlanTool, name)

    # 提示信息
    return "Request accepted. Running test plan '{}'...".format(name)


@app.route('/bash')
async def bash():
    css_style = '''
        <style>
            html, body {
                height: 100%;
                margin: 0;
            }
            body {
                background-color: black;
                color: #00ff00;
                display: flex;
                flex-direction: column;
                font-family: "Courier New", monospace;
                font-size: 14px;
                padding: 20px;
            }
            pre {
                white-space: pre-wrap;
                flex-grow: 1;
            }
            form {
                margin-top: 20px;
            }
            input[type="text"] {
                width: 100%;
                box-sizing: border-box;
            }
        </style>
        '''

    input_form = '''
        <pre id="output"></pre>
        <form id="command-form">
            <input type="text" id="command-input" placeholder="Enter command">
        </form>
        <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/3.1.3/socket.io.min.js"></script>
        <script>
            const socket = io();
            const commandForm = document.getElementById("command-form");
            const commandInput = document.getElementById("command-input");
            const output = document.getElementById("output");

            commandForm.addEventListener("submit", (event) => {
                event.preventDefault();
                const command = commandInput.value;
                commandInput.value = "";
                socket.emit("run_command", { command });
            });

            socket.on("command_output", (data) => {
                output.innerHTML += `> ${data.command}<br>${data.result}<br>`;
            });
        </script>
        '''

    return render_template_string(f'{css_style}{input_form}')


@socketio.on('run_command')
def handle_run_command(data):
    command = data['command']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    emit('command_output', {'command': command, 'result': result.stdout + result.stderr}, broadcast=True)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5001, debug=True)
    http_server = WSGIServer(('127.0.0.1', 5001), app)
    http_server.serve_forever()
