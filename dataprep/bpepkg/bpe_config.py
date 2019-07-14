from enum import Enum

from typing import Dict

from dataprep.prepconfig import PrepConfig, PrepParam


class BpeConfigNotSupported(Exception):
    pass


class BpeParam(str, Enum):
    CASE: str = 'case'
    WORD_END: str = 'wordend'
    BASE: str = 'base'
    UNICODE: str = 'unicode'


class BpeConfig(object):
    possible_param_values = {
        BpeParam.CASE: ['yes', 'no', 'prefix'],
        BpeParam.WORD_END: [True, False],
        BpeParam.BASE: ["all", "code", "java"],
        BpeParam.UNICODE: ['yes', 'no', 'bytes'],
    }

    @staticmethod
    def _check_param_number(n_passed_params: int):
        n_expected_params = len([i for i in BpeParam])
        if n_passed_params != n_expected_params:
            raise ValueError(f'Expected {n_expected_params} params, got {n_passed_params}')

    @staticmethod
    def _check_invariants(params: Dict[BpeParam, str]):
        BpeConfig._check_param_number(len(params))
        for pp in BpeParam:
            if params[pp] not in BpeConfig.possible_param_values[pp]:
                raise ValueError(f'Invalid value {params[pp]} for prep param {pp}, '
                                 f'possible values are: {BpeConfig.possible_param_values[pp]}')

    def __init__(self, params: Dict[BpeParam, str]):
        BpeConfig._check_invariants(params)

        self.params = params

    def get_param_value(self, param: BpeParam) -> str:
        return self.params[param]

    def to_prep_config(self):
        return PrepConfig({
            PrepParam.EN_ONLY: 'U' if self.get_param_value(BpeParam.UNICODE) == 'no' else 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'l' if self.get_param_value(BpeParam.CASE) == 'no' else 'u'
        })

    UNICODE_NO = '_nounicode'
    UNICODE_BYTES = '_bytes'
    CASE_NO = '_nocase'
    CASE_PREFIX = '_prefix'
    WORD_END = '_we'

    @staticmethod
    def from_suffix(suffix: str):
        if suffix.find(BpeConfig.CASE_NO) != -1:
            case = 'no'
        elif suffix.find(BpeConfig.CASE_PREFIX) != -1:
            case = 'prefix'
        else:
            case = 'yes'

        if suffix.find(BpeConfig.UNICODE_NO) != -1:
            unicode = 'no'
        elif suffix.find(BpeConfig.UNICODE_BYTES) != -1:
            unicode = 'bytes'
        else:
            unicode = 'yes'


        return BpeConfig({
            BpeParam.CASE: case,
            BpeParam.WORD_END: suffix.find(BpeConfig.WORD_END) != -1,
            BpeParam.BASE: 'code',
            BpeParam.UNICODE: unicode,
        })

    def to_suffix(self):
        suf = ''

        if self.get_param_value(BpeParam.CASE) == 'no':
            suf += BpeConfig.CASE_NO
        elif self.get_param_value(BpeParam.CASE) == 'prefix':
            suf += BpeConfig.CASE_PREFIX

        if self.get_param_value(BpeParam.WORD_END):
            suf += BpeConfig.WORD_END

        if self.get_param_value(BpeParam.UNICODE) == 'no':
            suf += BpeConfig.UNICODE_NO
        elif self.get_param_value(BpeParam.UNICODE) == 'bytes':
            suf += BpeConfig.UNICODE_BYTES

        return suf

    def __eq__(self, other):
        return self.params == other.params

    def __str__(self) -> str:
        res = ""
        for k in BpeParam:
            res += str(self.params[k])
        return res

    def __repr__(self):
        return str(self.params)