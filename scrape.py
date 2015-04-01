from __future__ import print_function
from collections import OrderedDict
import csv
import os
import re
import sys
import urllib

def scrape(todo_ids):
    def match(pattern, text):
        m = re.search(pattern, text)
        return m.group(1) if m else ''
    with open('database.csv', 'a') as doc:
        fieldnames = ['c_id', 'artist', 'track', 'album', 'song_url', 'filename']
        dw = csv.DictWriter(doc, delimiter=',', fieldnames=fieldnames)
        headers = OrderedDict()
        for fieldname in dw.fieldnames:
            headers[fieldname] = fieldname
        if os.path.getsize('database.csv') == 0:
            dw.writerow(headers)
        fail_counter = 0
        for c_num in todo_ids:
            info = OrderedDict()
            home = 'http://chordtabs.in.th/'
            info['c_id'] = 'c{:05}'.format(c_num)
            info['song_url'] = '{}song.php?song_id={}&chord=yes'.format(home, c_num)
            text = urllib.urlopen(info['song_url']).read()
            info['track'] = match(r'<span itemprop="track">(.+?)</span>', text)
            info['artist'] = match(r'<span itemprop="musicGroupMember">(.+?)</span>', text)
            info['album'] = match(r'<span itemprop="album">(.+?)</span>', text)
            if not (info['track'] and info['artist'] and info['album']):
                fail_counter += 1
                print('{} not found'.format(c_num))
                continue
            fail_counter = 0
            info['filename'] = home + match(r'<img src="./(admin/admin/songsxx/.+?)"', text)
            if not os.path.isdir('chords'):
                os.makedirs('chords')
            jpg_name = 'chords/{c_id} - {artist} - {track}.png'.format(**info)
            urllib.urlretrieve(info['filename'], jpg_name)
            dw.writerow(info)
            print(jpg_name)
    print('Done!')

def update():
    last_file = sorted(os.listdir('chords'), reverse=True)[0]
    last_id = int(re.search(r'c(\d\d\d\d\d).+?\.png', last_file).group(1))
    scrape(range(last_id + 1, last_id + 50))

def repeat():
    c_nums = []
    for png in os.listdir('chords'):
        c_num = int(re.search(r'c(\d\d\d\d\d).+?\.png', png).group(1))
        c_nums.append(c_num)
    missing_ids = sorted(list(set(range(10000, 20000)) - set(c_nums)))
    scrape(missing_ids)

def main():
    update()

if __name__ == '__main__':
    main()
