import requests
import zstandard as zstd
import gzip
import zlib
import json
import random
import string
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore
import sys
import requests
import zstandard as zstd
import gzip
import zlib
import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore
import sys
session = requests.Session()

def useragent():
    with open('userAgent.txt', 'r') as file:
        lines = file.read().splitlines()
        return random.choice(lines)

def generate_random_word():
    alphabets = 'zxcvbnmasdfghjkl'
    numbers = "987654321"
    
    # Generate the first two alphabetic characters
    word = ''.join(random.choices(alphabets, k=2))
    
    # Append a random number
    word += random.choice(numbers)
    
    # Append another alphabetic character
    word += random.choice(alphabets)
    
#    print(Fore.BLUE + f"{word}")
#    print(Fore.WHITE + "")
    
    return word

def decoder(response):
    content_encoding = response.headers.get('Content-Encoding')
    try:
        if content_encoding == 'gzip':
            return gzip.decompress(response.content).decode('utf-8')
        elif content_encoding == 'deflate':
            return zlib.decompress(response.content, -zlib.MAX_WBITS).decode('utf-8')
        elif content_encoding == 'zstd':
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(response.content).decode('utf-8')
        else:
            return response.text
    except zstd.ZstdError as e:
#        print(f"ZstdError: {e}")
        print(f"Content (truncated): {response.content[:500]}")
        return response.content.decode('utf-8')
    except (gzip.BadGzipFile, zlib.error) as e:
        print(f"DecompressionError: {e}")
        print(f"Content (truncated): {response.content[:100]}")
        return response.content.decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        print(f"Decoded content (truncated): {response.content[:100]}")
        return response.content.decode('utf-8')
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Content (truncated): {response.content[:500]}")
        return response.content.decode('utf-8')

def header_cookie():
    response = requests.post("https://www.instagram.com/accounts/signup/email/")
    cookies = response.cookies.get_dict()
    response = requests.get('https://www.instagram.com/api/v1/web/login_page/', cookies=cookies)
    csrftoken = response.cookies.get('csrftoken', '')
    ig_did = response.cookies.get('ig_did', '')
    mid = response.cookies.get('mid', '')
    return csrftoken, ig_did, mid, cookies

def username_availablity(user_agent, check_username, csrftoken, ig_did, mid, cookies):
    data = {'username': check_username}
    headers = {
        'User-Agent': user_agent,
        'Cookie': f'mid={mid}; ig_did={ig_did}; csrftoken={csrftoken}',
        'X-Csrftoken': csrftoken,
        'X-Ig-App-Id': '1217981644879628',
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = session.post('https://www.instagram.com/api/v1/users/check_username/', headers=headers, data=data, cookies=cookies)
    context = decoder(response)
    context_json = json.loads(context)
    if context_json.get('available') is False:
        print(Fore.RED + 'USERNAME IS TAKEN')
        print(Fore.WHITE + '\n')
    elif response.status_code == 429:
        print(Fore.RED + 'IP BLOCKED')
        print(Fore.WHITE + '\n')
    elif context_json.get('message') == 'CSRF token missing or incorrect':
        print(Fore.RED + "MISSING CSRF TOKEN")
        print(Fore.WHITE + '\n')
    else:
        print(Fore.GREEN + 'USERNAME AVAILABLE')
        print(Fore.WHITE + '\n')
        with open('4l_id.txt', 'a') as file:
            file.write(check_username + '\n')

def main():
    csrftoken, ig_did, mid, cookies = header_cookie()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i in range(40):  # Change to 35 iterations
            if i % 15 == 0 and i != 0:  # Update every 15 iterations
                csrftoken, ig_did, mid, cookies = header_cookie()
            check_username = generate_random_word()
            user_agent = useragent()
            futures.append(executor.submit(username_availablity, user_agent, check_username, csrftoken, ig_did, mid, cookies))
            if i == 40:  # Exit after 35 iterations
                sys.exit()
        for future in as_completed(futures):
            future.result()  # Process results if needed

if __name__ == "__main__":
    main()
