"""Version a presentation-only HTML derivative without changing export identity."""
import re
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / 'hosting/production'


def render(generated, build):
    if not re.fullmatch(r'[0-9a-f]{64}', build):
        raise ValueError('Invalid build ID')
    replacements = {
        '<head>': f'<head>\n<base href="/builds/{build}/">',
        '</head>': '<style>\n' + (CONFIG / 'shell.css').read_text() + '</style>\n</head>',
        '<canvas id="canvas">': '<canvas id="canvas" width="1280" height="720" tabindex="0">',
        '"canvasResizePolicy":1': '"canvasResizePolicy":0',
        '<script src="index.js"></script>':
            '<button id="fullscreen" type="button" title="Enter fullscreen" hidden>Fullscreen</button>\n'
            '<script>\n' + (CONFIG / 'shell.js').read_text() + '</script>\n'
            '<script src="index.js"></script>',
    }
    for before, after in replacements.items():
        if generated.count(before) != 1:
            raise ValueError('Unexpected generated shell layout: ' + before)
        generated = generated.replace(before, after, 1)
    return generated.encode('utf-8')
