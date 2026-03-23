#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app.py — Servidor Flask para el Extractor de Fechas Blog Telcel
Uso: python app.py  →  http://localhost:5001
"""

import os
import subprocess
import sys
from flask import Flask, Response, render_template, stream_with_context, jsonify

app     = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOP_FILE = os.path.join(BASE_DIR, 'stop_signal.txt')

_state = {'process': None}


def _make_env():
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    return env


def _stream_script(script_name):
    """Genera un SSE stream corriendo script_name como subproceso."""
    def generate():
        process = subprocess.Popen(
            [sys.executable, script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            cwd=BASE_DIR,
            env=_make_env(),
        )
        _state['process'] = process

        try:
            for line in process.stdout:
                yield f"data: {line.rstrip()}\n\n"
        except GeneratorExit:
            process.terminate()
            _state['process'] = None
            return

        process.wait()
        _state['process'] = None
        yield "event: done\ndata: \n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control':    'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection':       'keep-alive',
        },
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stream-urls')
def stream_urls():
    """Paso 1: scraper que genera urls_a_procesar.txt."""
    return _stream_script('scraper_urls.py')


@app.route('/stream-fechas')
def stream_fechas():
    """Paso 2: extractor de fechaNota por URL."""
    return _stream_script('extractor_selenium.py')


@app.route('/stop', methods=['POST'])
def stop():
    """Crea stop_signal.txt para que el script activo guarde y salga."""
    open(STOP_FILE, 'w').close()
    return jsonify({'ok': True})


if __name__ == '__main__':
    print("=" * 55)
    print("  Extractor de Fechas — Blog Telcel")
    print("  http://localhost:5001")
    print("=" * 55)
    app.run(debug=False, threaded=True, port=5001)
