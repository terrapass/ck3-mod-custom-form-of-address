#!/usr/bin/env python
import argparse
import traceback
from pathlib import Path
from os import path

import yaml
from jinja2 import Environment, FileSystemLoader

#
# Constants
#

CLI_DESCRIPTION = 'Renders all Jinja templates in a directory into files in another directory, preserving the folder structure.'

SOURCE_ENCODING = 'utf_8_sig' # UTF-8 with BOM
TARGET_ENCODING = 'utf_8_sig' # UTF-8 with BOM

TEMPLATE_EXTENSION = '.jinja'
TEMPLATE_GLOB      = '**/*' + TEMPLATE_EXTENSION

#
# Command line arguments
#

parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)

parser.add_argument('source_path', metavar='SOURCE_PATH', type=Path, help='root directory containing Jinja templates')
parser.add_argument('target_path', metavar='TARGET_PATH', type=Path, help='target root directory for rendered files')
parser.add_argument('--vars',      metavar='VARS_YAML',   type=Path, help='YAML file containing template variable definitions')

parser.add_argument('-v', '--verbose', action='store_true', dest='is_verbose', help='output processed file paths to stdout')

args = parser.parse_args()

#
# Service
#

def load_vars_from_yaml_file(vars_file_path: Path) -> dict:
    with open(vars_file_path, 'r') as vars_file:
        return yaml.load(vars_file, Loader=yaml.FullLoader)

def render_dir(jinja_env: Environment, source_path: Path, target_path: Path, vars: dict, is_verbose: bool):
    templates_paths = source_path.glob(TEMPLATE_GLOB)
    for template_path in templates_paths:
        template_name    = source_template_path_to_name(source_path, template_path)
        target_file_path = template_name_to_target_file_path(target_path, template_name)

        if is_verbose:
            print(target_file_path)

        render_to_file(jinja_env, template_name, target_file_path, vars)

def render_to_file(jinja_env: Environment, template_name: str, target_file_path: Path, vars: dict):
    template = jinja_env.get_template(template_name)
    rendered_content = template.render(vars)
    with open(target_file_path, 'w', encoding=TARGET_ENCODING) as target_file:
        target_file.write(rendered_content)

def source_template_path_to_name(source_dir_path: Path, template_path: Path) -> str:
    return path.relpath(template_path, source_dir_path).replace('\\', '/')

def template_name_to_target_file_path(target_dir_path: Path, template_name: str) -> Path:
    assert template_name.endswith(TEMPLATE_EXTENSION)
    return target_dir_path / template_name[:-len(TEMPLATE_EXTENSION)]

#
# Main
#

jinja_env = Environment(
    loader=FileSystemLoader(args.source_path, encoding=SOURCE_ENCODING),
    autoescape=False
)

vars = load_vars_from_yaml_file(args.vars) if not args.vars is None else dict()

try:
    render_dir(jinja_env, args.source_path, args.target_path, vars, args.is_verbose)
except TypeError:
    traceback.print_exc()
    print('hint: if your templates use variables, make sure you defined all of them in the YAML file given via --vars argument')
    exit(1)
