from requests import get


class Version:

    def __init__(self, version: str) -> None:
        self.version = tuple(map(int, version.split('.')))
    
    def __gt__(self, other) -> bool:
        for i in range(min(len(self.version), len(other.version))):
            if self.version[i] > other.version[i]:
                return True
            elif self.version[i] < other.version[i]:
                return False
        return len(self.version) > len(other.version)

    def __lt__(self, other) -> bool:
        for i in range(min(len(self.version), len(other.version))):
            if self.version[i] < other.version[i]:
                return True
            elif self.version[i] > other.version[i]:
                return False
        return len(self.version) < len(other.version)

    def __eq__(self, other) -> bool:
        return self.version == other.version

    def __ge__(self, other) -> bool:
        return self > other or self == other

    def __le__(self, other) -> bool:
        return self < other or self == other

    def __ne__(self, other) -> bool:
        return not self == other

    def __str__(self) -> str:
        return '.'.join(map(str, self.version))


class UpdateChecker:

    target_url = 'https://github.com/R1senDev/AikoProject/releases/latest'
    current_version = '0.0.2'

    @classmethod
    def check(cls, verbose: bool = False) -> dict[str, bool | str]:

        response = get(cls.target_url)

        ok = False
        latest_release_version = cls.current_version
        update_available = False

        if response.status_code == 200:
            ok = True
            latest_release_version = response.url.split('/')[-1]
            update_available = Version(latest_release_version) > Version(cls.current_version)
        
        return {
            'ok': ok,
            'latest_version': latest_release_version,
            'update_available': update_available
        }


__all__ = [
    'UpdateChecker'
]


if __name__ == '__main__':
    print(UpdateChecker.check())