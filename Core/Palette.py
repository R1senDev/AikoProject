'''
Core.Palette
for AikoProject
'''


from colorama import init, Fore, Back, Style
from typing   import Hashable

init()


class ColorPreset:

    def __init__(self, *args) -> None:
        self._str = ''.join(args)

    def __enter__(self):
        print(self._str, end = '')
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        print(Style.RESET_ALL, end = '')
        return self


presets = {} # type: dict[Hashable, ColorPreset]


__all__ = [
    'Fore',
    'Back',
    'Style',
    'ColorPreset',
    'presets'
]