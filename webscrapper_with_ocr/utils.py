import urllib.request
from PIL import Image
from urllib.error import HTTPError
from typing import List

def image_downloader(urls : List, target_path : str):
    for cnt, url in enumerate(urls):
        file_name = target_path + f'/{cnt}.png'
        try:
            urllib.request.urlretrieve(url, file_name)
        except Exception as e:
            print(e)
            print("please provide a valid URL")




# if __name__ == "__main__":

    # image_downloader('https://m.media-amazon.com/images/I/61HtE5BWXRL._SL1424_.jpg', 'demo2.png')

