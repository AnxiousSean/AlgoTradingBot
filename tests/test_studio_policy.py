"""Static check mirroring TradeLocker Studio's code security policy.

Known-blocked items come from Studio's own error messages. 'Suspected' items
are builtins sandboxes usually block; we avoid them pre-emptively.
"""
import ast
import os

import pytest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
STUDIO_FILES = ['probe/probe_bot.py']

BLOCKED_IMPORTS = {'sys', 'zoneinfo'}                       # confirmed by Studio
SUSPECT_IMPORTS = {'os', 'subprocess', 'importlib', 'builtins', 'socket',
                   'requests', 'urllib', 'pickle', 'inspect', 'platform'}
BLOCKED_CALLS = {'getattr'}                                 # confirmed by Studio
SUSPECT_CALLS = {'setattr', 'delattr', 'eval', 'exec', 'compile', 'open',
                 '__import__', 'globals', 'locals', 'vars', 'input', 'breakpoint'}
# Imports Studio accepted (not flagged when probe imported them):
ALLOWED_IMPORTS = {'backtrader', 'math', 'datetime', 'collections', 'statistics',
                   'numpy', 'pandas', 'time'}


@pytest.mark.parametrize('rel', STUDIO_FILES)
def test_studio_policy(rel):
    tree = ast.parse(open(os.path.join(ROOT, rel)).read())
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else [node.module or ''])
            for n in names:
                top = n.split('.')[0]
                if top in BLOCKED_IMPORTS | SUSPECT_IMPORTS or top not in ALLOWED_IMPORTS:
                    problems.append('line %d: import %s' % (node.lineno, n))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in BLOCKED_CALLS | SUSPECT_CALLS:
                problems.append('line %d: call %s()' % (node.lineno, node.func.id))
    assert not problems, '\n'.join(problems)
