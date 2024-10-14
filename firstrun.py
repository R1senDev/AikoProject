from os.path import exists
from json    import load, dump


def init() -> tuple[dict[str, str], bool]:

    with open('files.json', 'r') as file:
        files = load(file)
    
    nf_count = 0
    paths = {} # type: dict[str, str]

    for key in files:
        fname = files[key]['path']
        paths[key] = fname
        if not exists(fname):
            if isinstance(files[key]['default'], str):
                print(f'Creating: {fname}')
                nf_count += 1
                with open(fname, 'w', encoding = 'utf-8') as file:
                    file.write(files[key]['default'])
    
    return (paths, nf_count > 0)