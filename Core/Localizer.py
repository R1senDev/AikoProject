'''
Core.Localizer
for AikoProject
'''


from warnings import warn
from json     import load


class LocalizationFileError(Exception): ...


_current_locale_name = 'empty_pack'
_current_locale_dict = {}
lang_path = 'languages/{}.json'


def set_locale(name: str) -> int:
    global _current_locale_dict

    if name == 'empty_pack':
        raise LocalizationFileError(f'Locale "{name}" is reserved')

    if name == _current_locale_name:
        return len(_current_locale_dict.keys())
        
    try:
        with open(lang_path.format(name), 'r', encoding = 'utf-8') as file:
            _current_locale_dict = load(file)
    except:
        raise LocalizationFileError(f'unable to load {lang_path.format(name)}')
    
    return len(_current_locale_dict.keys())


def locstr(str_name: str, nf_warn: bool = True) -> str:
    if str_name in _current_locale_dict:
        return _current_locale_dict[str_name]
    if nf_warn:
        warn(f'String "{str_name}" not found in pack "{_current_locale_name}"')
    return str_name