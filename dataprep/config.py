import os

import appdirs

TRAIN_DIR = 'train'
TEST_DIR = 'test'
VALID_DIR = 'valid'

CASE_DIR='case'
NO_CASE_DIR='nocase'

REPR_DIR = 'repr'
PARSED_DIR = 'parsed'
BPE_DIR = 'bpe'

current_script_location = os.path.realpath(__file__)
root_package_dir = os.path.dirname(current_script_location)
data_dir = os.path.join(root_package_dir, 'data')

app_name='dataprep'

with open(os.path.join(root_package_dir, 'VERSION')) as version_file:
    version = version_file.read().strip()

USER_CONFIG_DIR = appdirs.user_config_dir(app_name, appauthor=False, version=version)
USER_CACHE_DIR = appdirs.user_cache_dir(app_name, appauthor=False, version=version)

DEFAULT_PARSED_DATASETS_DIR = os.path.join(USER_CACHE_DIR, 'prep_datasets')
DEFAULT_BPE_DIR = os.path.join(data_dir, BPE_DIR)
DEFAULT_BPE_CACHE_DIR = os.path.join(USER_CACHE_DIR, BPE_DIR)

REWRITE_PARSED_FILE=False