#!/usr/bin/env python
import os
path = os.getcwd()
for prefix, dirs, files in os.walk(path):
    for name in files:
        if name.endswith('.pyc') or name.endswith('.pyo'):
            filename = os.path.join(prefix, name)
            os.remove(filename)
