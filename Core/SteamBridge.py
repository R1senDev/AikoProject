'''
Core.SteamBridge
for AikoProject
'''


from fuzzywuzzy import fuzz
from webbrowser import open as open_url
from warnings   import warn
from typing     import Literal
from os         import walk, path
from re         import search


class SteamLaunchError(Exception): ...


class SteamLibrary:

    def __init__(self, lib_path: str) -> None:
        self._lib_path = lib_path
        self._installed_games_cache = {} # type: dict[int, str]
        self.update_installed_games_list()

    def run_game_by_id(self, game_id: int) -> Literal[True]:
        '''
        Opens steam://rungameid/{game_id}.

        :param game_id: Steam game ID.
        '''

        if game_id not in self._installed_games_cache:
            raise SteamLaunchError(f'game with id={game_id} seems not installed')
        
        url = f'steam://rungameid/{game_id}'
        open_url(url)

        return True

    def update_installed_games_list(self) -> dict[int, str]:
        '''
        Guess what.
        '''

        games_dict = {}

        for root, dirs, files in walk(self._lib_path):
            for file in files:
                if file.startswith('appmanifest'):
                    manifest_path = path.join(root, file)
                    with open(manifest_path, 'r', encoding = 'utf-8', errors = 'ignore') as f:
                        content = f.read()
                        match_id = search(r'"appid"\s+"(\d+)"', content)
                        match_name = search(r'"name"\s+"([^"]+)"', content)
                        if match_id and match_name:
                            game_id = int(match_id.group(1))
                            game_name = match_name.group(1)
                            games_dict[game_id] = game_name

        self._installed_games_cache = games_dict
        return games_dict

    def run_game_by_name(self, game_name: str) -> bool:
        '''
        Finds game using fuzz and runs it.

        :param game_name: Game name.
        '''

        best_match = None
        best_score = 0

        for game_id, name in self._installed_games_cache.items():
            score = fuzz.ratio(game_name.lower(), name.lower())
            if score > best_score:
                best_score = score
                best_match = game_id

        if best_match:
            self.run_game_by_id(best_match)
        else:
            warn(f'Game "{game_name}" not found (seems not installed)')
            return False
        
        return True