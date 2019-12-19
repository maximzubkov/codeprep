from enum import Enum, auto
from typing import List, Tuple, Optional

from dataprep.parse.model.core import ParsedSubtoken, with_empty_metadata, ParsedToken, unwrap_single_string
from dataprep.parse.model.metadata import PreprocessingMetadata
from dataprep.parse.model.placeholders import placeholders
from dataprep.preprocess.core import ReprConfig


class Capitalization(Enum):
    UNDEFINED = auto()
    NONE = auto()
    FIRST_LETTER = auto()
    ALL = auto()


class Underscore(ParsedSubtoken):
    def __eq__(self, other):
        return other.__class__ == self.__class__

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def __str__(self):
        return self.non_preprocessed_repr()[0]

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> [Tuple[str, PreprocessingMetadata]]:
        return with_empty_metadata("_")


class Word(ParsedSubtoken):
    """
    Invariants:
    str === str(Word.of(str))
    """

    def __init__(self, canonic_form: str, capitalization: Capitalization = Capitalization.UNDEFINED):
        Word._check_canonic_form_is_valid(canonic_form)

        self.canonic_form = canonic_form
        self.capitalization = capitalization

    def get_canonic_form(self) -> str:
        return self.canonic_form

    @staticmethod
    def _is_strictly_upper(s) -> bool:
        return s.isupper() and not s.lower().isupper()

    @staticmethod
    def _check_canonic_form_is_valid(canonic_form) -> None:
        if not isinstance(canonic_form, str) or Word._is_strictly_upper(canonic_form) \
                or (canonic_form and Word._is_strictly_upper(canonic_form[0])):
            raise AssertionError(f"Bad canonic form: {canonic_form}")

    def __str__(self):
        return unwrap_single_string(self.non_preprocessed_repr())

    def __with_capitalization_prefixes(self, subwords: List[str]) -> List[str]:
        if self.capitalization == Capitalization.UNDEFINED or self.capitalization == Capitalization.NONE:
            res = subwords
        elif self.capitalization == Capitalization.FIRST_LETTER:
            res = [placeholders['capital']] + subwords
        elif self.capitalization == Capitalization.ALL:
            res = [placeholders['capitals']] + subwords
        else:
            raise AssertionError(f"Unknown value: {self.capitalization}")
        return res

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        if repr_config.should_lowercase:
            subwords = repr_config.word_splitter(self.canonic_form, repr_config.bpe_data)
            subwords_with_prefix = self.__with_capitalization_prefixes(subwords)
            return with_empty_metadata(subwords_with_prefix)
        else:
            subwords = repr_config.word_splitter(self.__with_preserved_case(), repr_config.bpe_data)
            return with_empty_metadata(subwords)

    def __with_preserved_case(self) -> str:
        if self.capitalization == Capitalization.UNDEFINED or self.capitalization == Capitalization.NONE:
            return self.canonic_form
        elif self.capitalization == Capitalization.FIRST_LETTER:
            return self.canonic_form.capitalize()
        elif self.capitalization == Capitalization.ALL:
            return self.canonic_form.upper()
        else:
            raise AssertionError(f"Unknown value: {self.capitalization}")

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        return with_empty_metadata([self.__with_preserved_case()])

    def __repr__(self):
        return f'{self.__class__.__name__}({self.canonic_form, self.capitalization})'

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.canonic_form == other.canonic_form \
               and self.capitalization == other.capitalization

    @classmethod
    def from_(cls, s: str):
        if not s:
            raise ValueError(f'A subword can be neither None nor of length zero. Value of the subword is {s}')

        if s.islower() or not s:
            return cls(s, Capitalization.NONE)
        elif s.isupper():
            return cls(s.lower(), Capitalization.ALL)
        elif s[0].isupper():
            return cls(s[0].lower() + s[1:], Capitalization.FIRST_LETTER)
        else:
            return cls(s, Capitalization.UNDEFINED)


class NonProcessibleToken(ParsedToken):
    def __init__(self, token: str):
        self.token = token

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.token == other.token

    def __repr__(self):
        return f'{self.__class__.__name__}({self.token})'

    def __str__(self):
        return self.token

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        return self.wrap_in_metadata_for_full_word([self.token], non_proc={self.token})


class KeyWord(NonProcessibleToken):
    def __init__(self, token: str):
        super().__init__(token)


class Operator(NonProcessibleToken):
    def __init__(self, token: str):
        super().__init__(token)


class NonCodeChar(NonProcessibleToken):
    def __init__(self, token: str):
        super().__init__(token)


class SpecialToken(NonProcessibleToken):
    def __init__(self, token: str):
        super().__init__(token)
