# by Henry Zhang (@henryz)
# 2020-06-29

import glob
import os
import shutil
import re

doc_root = "docs/"

# move all asset files
source = '.gitbook/assets/'
dest = 'images/'

if not os.path.exists(doc_root + dest):
    os.makedirs(doc_root + dest)

if os.path.exists(doc_root + source):
    for file in os.listdir(doc_root + source):
        shutil.move(doc_root + source + file, doc_root + dest)

    os.rmdir(doc_root + source)
    os.rmdir(doc_root + '.gitbook/')

# remove .github folder
if os.path.exists(doc_root + ".github/"):
    shutil.rmtree(doc_root + ".github")

# replace gitbook hint and file extensions to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% hint style="warning" %}
# some text
# {% endhint %}
# --------- to ---------
# !!! warning
#     some text

os.chdir(doc_root)

gb_hint_rg = r'{% hint style=\"(.*)\" %}(.*|[\s\S]+?){% endhint %}'


def hint_group(groups):
    hint_type = groups.group(1)
    hint_content = groups.group(2)
    hint_content = hint_content.replace("\n", "\n\t")
    return "!!! " + hint_type + "\n" + hint_content


for md_file in glob.glob("*.md"):
    with open(md_file, 'r') as file:
        filedata = file.read()

    filedata = filedata.replace(source, dest)
    filedata = re.sub(gb_hint_rg, hint_group, filedata)

    with open(md_file, 'w') as file:
        file.write(filedata)


# replace nav with SUMMARY.md
subpage_match_rg = r'## (.*)\n(.*|[\s\S]+?)(\Z|(?=##))'


def subpage_group(groups):
    title = groups.group(1)
    title = re.sub(" <a.*>", "", title)
    content = groups.group(2)
    content = content.replace("- ", "  - ")
    return "  - " + title + ":\n" + content


with open('SUMMARY.md', 'r') as file:
    nav_content = file.read()

nav_content = nav_content.replace('# Table of contents', 'nav:')
nav_content = nav_content.replace('\n\n', '\n')
nav_content = re.sub(r"\* \[(.*)\]\((.*)\)", r"  - \1: \2", nav_content)
nav_content = re.sub(subpage_match_rg, subpage_group, nav_content)

# write nav changes to yml
# please add '# [AUTO-INJECT-NAV]' to your mkdocs.yml

os.chdir('..')

with open('mkdocs.yml', 'r') as file:
    yml = file.read()

yml = yml.replace('# [AUTO-INJECT-NAV]', nav_content)

with open('mkdocs.yml', 'w') as file:
    file.write(yml)
