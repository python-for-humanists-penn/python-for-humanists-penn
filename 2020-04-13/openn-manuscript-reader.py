#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 12:33:00 2020

@author: davidnelson
"""

# test using LJS465, collection ID 0001
# download images and metadata X
# run via wget using subprocess run() to get images X
# $ wget -nd -np -r -A_web.jpg -A.xml -P openn/ljs225 \
#       http://openn.library.upenn.edu/Data/0001/ljs225/
# getting TEI: use requests? or just wget
# using wget - will need to save and read, parse with bs4
# using requests - will save as memory
# user can provide input to pick what manuscript they want
# identify relevant metadata for creating ebook
# ????
# ????
# plug into EbookLib to make ebook
# Profit!
# https://pypi.org/project/EbookLib/

import subprocess
from bs4 import BeautifulSoup as soup
from ebooklib import epub
import os

repo_num = input(
        'Please enter the collection ID for the manuscript from Openn: ')
ms_name = input('Please enter the manuscript call number from Openn: ')

command = ['wget', '-nd', '-np', '-r', '-A', '_web.jpg', '-A.xml', '-P',
           ms_name,
           f'http://openn.library.upenn.edu/Data/{repo_num}/{ms_name}/']

subprocess.run(command)

with open(f'{ms_name}/{ms_name}_TEI.xml') as f:
    soup = soup(f, 'xml')  # specify 'xml' so it parses data correctly

# minimum metadata required for epub: identifier, title, language


book = epub.EpubBook()

# get bibid, if it exists
bibid = soup.find('altIdentifier', attrs={'type': 'bibid'})
if bibid is None:
    call_number = soup.find('idno', attrs={'type': 'call-number'})
    identifier = 'openn' + call_number.string
else:
    identifier = 'openn' + bibid.idno.string

print('Preparing book metadata...')

book.set_identifier(identifier)

ms_item = soup.find('msItem')  # assuming title is first <title> tag in first
                               # <msItem> tag
ms_title = ms_item.title.string

book.set_title(ms_title)

# get ISO language code. Is this the correct controlled vocabulary?
ms_lang = soup.textLang['mainLang']

book.set_language(ms_lang)

ms_authors = ms_item.find_all('author')

for i in ms_authors:
    author = i.persName.string
    # vernac = i.find('persName', attrs={'type': 'vernacular'})
    # vernac_auth = vernac.string
    print(author)
    book.add_author(author)
    # book.add_author(vernac_auth, uid='vernacular')

# get list of images

image_list = []
file_list = os.listdir(ms_name)
for f in file_list:
    if 'REF' in f:
        continue
    elif f.endswith('jpg'):
        image_list.append(f)

image_list.sort()
print(image_list)

# first image is cover 

book.set_cover(f'{ms_name}/{image_list[0]}', open(f'{ms_name}/{image_list[0]}', 'rb').read())

# var_holder = {}

# for i in range(10):
#    var_holder['my_var_' + str(i)] = "iterationNumber=="+str(i)

# locals().update(var_holder)

# image_holder = {}

image_html = []
for i in image_list[1:]:
    image_src = f'<img src="{ms_name}/{i}">'
    image_html.append(image_src)

image_content = '<html><head></head><body>' + ''.join(image_html) + '</body></html>'

n = 1
images = epub.EpubHtml(title=f'images', file_name=f'images.xhtml')
images.content = image_content

for image in image_list[1:]:
    file_name = f'image{n}'
    ei = epub.EpubImage()
    ei.file_name = f'{ms_name}/{image}'
    ei.media_type = 'image/jpeg'
    ei.content = open(f'{ms_name}/{image}', 'rb').read()
    book.add_item(ei)
    n = n + 1

# locals().update(image_holder)
# for item in image_holder.keys():
#    book.add_item(item)
#    spine_info.append(item)
#    item.content = f'<html><head></head><body><img src="{ms_name}/{image}"></body></html>'


# find more robust ereader to see if multiple authors can be set

# create chapter
# c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='hr')
# c1.content=u'<h1>Intro heading</h1><p>Zaba je skocila u baru.</p>'

# add chapter
# book.add_item(c1)

# book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
#             (epub.Section('Simple book'),
#             (c1, ))
#            )

# add default NCX and Nav file
print('I got to line 150!')
book.add_item(epub.EpubNcx())  # required element
book.add_item(epub.EpubNav())  # required element

# define CSS style
# style = 'BODY {color: white;}'
# nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

# add CSS file
# book.add_item(nav_css)

# basic spine
print('I got to line 162!')
book.spine = ['nav', images]  # required element

print("I'm making your book now! So friendly!")

epub.write_epub(f'{ms_name}.epub', book, {})

# for next time: additional metadata? start working on getting images
