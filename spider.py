import os
import zipfile
import requests
from problemconfconverter import *

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52',
    'Cookie': ''
}

config=None
basepath=None
def init():
    global basepath
    basepath = os.path.join(os.path.dirname(__file__), config.basepath)
    if not os.path.exists(basepath):
        os.mkdir(basepath)


def get_data(id):
    r = requests.get(f'{config.url}/download.php?type=data&id={id}',
                     headers=headers)
    print(f'start to config data of {config.pre}{id}')
    if r.status_code == 404:
        print('404 Error')
        return False

    p = os.path.join(basepath, f'{config.pre}{id}/')
    with open(os.path.join(p, 'dat.zip'), 'wb') as f:
        f.write(r.content)
    with zipfile.ZipFile(os.path.join(p, 'dat.zip')) as zf:
        zf.extractall(p)
    if os.path.exists(os.path.join(p, 'testdata')):
        os.system('rd /s /q "'+os.path.join(p, 'testdata')+'"')
    os.rename(os.path.join(p, str(id)), os.path.join(p, 'testdata'))
    os.remove(os.path.join(p, 'dat.zip'))

    if not convert(os.path.join(p, 'testdata')):
        return False
    print(f'convert {config.pre}{id} successfully')
    return True


def problem_count():
    l = 1
    r = 100000
    while l < r:
        mid = (l+r+1) >> 1
        if requests.get(f'{config.url}/problem/{mid}', headers=headers).status_code == 404:
            r = mid-1
        else:
            l = mid
    return l


def download_problem(id_):
    name = f'{config.pre}{id_}'
    p = os.path.join(basepath, f'{name}')
    if os.path.exists(p):
        if config.skip:
            return
        os.system(f'rd /s /q "{p}"')
    os.mkdir(p)

    print(f'start to download problem {id_}')
    page = requests.get(
        f'{config.url}/problem/{id_}/manage/statement', headers=headers).text
    title = re.search('<title>(.*?)</title>',
                      page).group(1).split('-')[0].strip(' ')
    md = re.search('<textarea class="form-control" name="problem_content_md" id="input-problem_content_md">(.*?)</textarea>',
                   page, re.DOTALL).group(1)
    tags = re.search('<input type="text" class="form-control" name="problem_tags" id="input-problem_tags" value="(.*?)" />',
                     page, re.DOTALL).group(1).split(',')
    tags = [tag.strip(' ') for tag in tags]
    tags.extend(config.extags)
    if not tags:
        tags = config.defaulttags
    
    if not md or not get_data(id_):
        os.system(f'rd /s /q "{p}"')
        return

    with open(os.path.join(p, 'problem.yaml'), 'w', encoding='utf-8') as f:
        f.write(config.templ
                .replace('{pid}', name)
                .replace('{title}', title)
                .replace('{tags}', '\n' .join(['  - '+tag for tag in tags]))
                )
    with open(os.path.join(p, f'problem_ch.md'), 'w', encoding='utf-8') as f:
        f.write(md)
    with open(os.path.join(p, f'problem_en.md'), 'w', encoding='utf-8') as f:
        f.write(md)


def download(id_):
    for cnt in range(config.retry_cnt):
        try:
            download_problem(id_)
            return
        except PermissionError:
            pass
        except FileNotFoundError as e:
            print(e)
            break
        # except Exception as e:
        #     print(e)
    print(f"Failed on problem {id_}")



def main():
    global config
    headers['Cookie'] = f'UOJSESSID={input("Cookie: UOJSESSID=")}'
    config=__import__(input('ConfigModule: '))
    init()
    while True:
        opt = input('> ').split(' ')
        if opt[0] == 'all':
            cnt = problem_count()
            for i in range(1, cnt+1):
                download(i)
        elif opt[0] == 'ps':
            for id_ in opt[1:]:
                download(id_)
        elif opt[0][:4] == 'set-':
            var = opt[0].split('-')[1]
            exec(f'global {var}\n{var}={opt[1]}')
        elif opt[0] == 'cookie':
            headers['Cookie'] = f'UOJSESSID={opt[1]}'
        elif opt[0]=='quit':
            break

main()
