# This script automatically formats all .py files in the specified directory 

import os
import subprocess

def main(dir_path):
    for subdir, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(subdir, file)
                cmd = ['autopep8', '--in-place', '--recursive', filepath]
                subprocess.call(cmd)

dir_path = 'auto_gpt_workspace'
main(dir_path)