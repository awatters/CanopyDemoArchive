
"""
Package a directory as a demo.

Look for a file named icon.(gif|png|jpg) as the icon.
Package any *.py file or any directory containing an __init__.py
as code.
All other files assume to be data files
"""

import os
import os.path
import shutil
import json

LOCAL_DEMO_DIRECTORY = "~/canopy_demos"

def install_demo(from_directory, demo_id, demo_name, 
                 tags=("General",), version=1.0):
    demos_dir = os.path.expanduser(LOCAL_DEMO_DIRECTORY)
    if not os.path.isdir(demos_dir):
        os.mkdir(demos_dir)
    to_directory = os.path.join(demos_dir, demo_id)
    demo_metadata = stage(demo_name, from_directory, to_directory,
                          version)
    all_metadata = archive_demo_metadata_locally(demo_id, tags)
    return all_metadata

def zip_up(directory_name, base_dir):
    #print "zip", (directory_name, base_dir)
    base_name = os.path.join(base_dir, directory_name)
    #print "zipping", directory_name, "in", base_dir, "to", base_name, ".zip"
    return shutil.make_archive(base_name=base_name, 
                               format="zip", 
                               root_dir=base_dir,
                               base_dir=directory_name)

def stage(demo_name, directory, staging_directory, version=1.0):
    if os.path.isdir(staging_directory):
        shutil.rmtree(staging_directory)
    os.mkdir(staging_directory)
    icon = None
    code = []
    data = []
    analysis = analyze(directory)
    for name in analysis:
        new_name = name
        (path, category, is_dir) = analysis[name]
        dest_path = os.path.join(staging_directory, name)
        if is_dir:
            #print "copytree", (path, dest_path)
            #os.mkdir(dest_path)
            shutil.copytree(path, dest_path)
            zip_up(name, staging_directory)
            new_name = name+".zip"
        else:
            shutil.copy(path, dest_path)
        entry = { "local": new_name }
        if category=="data":
            data.append(entry)
        if category=="code":
            code.append(entry)
        if category=="icon":
            icon = entry
    if icon is None:
        iconfn = "icon.png"
        iconpath = os.path.join(staging_directory, iconfn)
        make_icon(demo_name, iconpath)
        icon = { "local": iconfn }
    metadata = {
        "Name": demo_name,
        "version": version,
        "icon": icon, 
        "code": code, 
        "data": data}
    metadatafn = os.path.join(staging_directory, "metadata.json")
    with open(metadatafn, "w") as f:
        json.dump(metadata, f, indent=4)
    return metadata

def analyze(directory):
    """
    return analysis of files in directory as
    {filename: (path, category, is_dir), ...}
    where category is "data" or "code" or "icon"
    """
    result = {}
    ls = os.listdir(directory)
    for name in ls:
        path = os.path.join(directory, name)
        is_dir = os.path.isdir(path)
        if is_dir:
            category = "data" # default
            iname = os.path.join(directory, name, "__init__.py")
            if os.path.isfile(iname):
                category = "code"
        else:
            category = "data" # default
            if name.endswith(".py"):
                category = "code"
            if name in ["icon.jpg", "icon.gif", "icon.png"]:
                category = "icon"
        result[name] = (path, category, is_dir)
    return result

def archive_demo_metadata_locally(demo_id, tags=("General",)):
    demos_dir = os.path.expanduser(LOCAL_DEMO_DIRECTORY)
    if not os.path.isdir(demos_dir):
        raise ValueError, "no demos directory found at "+repr(demos_dir)
    all_metadata_fn = os.path.join(demos_dir, "demo_metadata.json")
    this_directory = os.path.join(demos_dir, demo_id)
    if not os.path.isdir(this_directory):
        raise ValueError, "no demo information found at "+repr(this_directory)
    this_metadata_fn = os.path.join(demos_dir, demo_id, "metadata.json")
    if os.path.isfile(all_metadata_fn):
        with open(all_metadata_fn) as f:
            all_metadata = json.load(f)
    else:
        all_metadata = []
    with open(this_metadata_fn) as f:
        this_metadata = json.load(f)
    def expand_filenames(d):
        result = {}
        for k in d:
            fn = d[k]
            path = os.path.join(this_directory, fn)
            result[k] = path
        return result
    prepared_metadata = {}
    prepared_metadata["Id"] = demo_id
    prepared_metadata["Name"] = this_metadata["Name"]
    prepared_metadata["downloaded"] = True
    prepared_metadata["version"] = this_metadata.get("version", 1)
    prepared_metadata["tags"] = tags
    prepared_metadata["icon"] = expand_filenames( this_metadata["icon"] )
    for k in ("code", "data"):
        if k in this_metadata:
            prepared_metadata[k] = map( expand_filenames, this_metadata[k] )
    augmented_metadata = all_metadata[:]
    augmented_metadata.append(prepared_metadata)
    with open(all_metadata_fn, "w") as f:
        json.dump(augmented_metadata, f, indent=4)
    return augmented_metadata

def make_icon(name, path, minlen=4, maxlen=12, maxheight=5, dy=30):
    from skimpyGimpy import canvas
    lines = []
    words = name.split()
    lineLen = max( map(len, words) ) + 1
    lineLen = max( lineLen, len(name)/maxheight )
    lineLen = max(lineLen, minlen)
    lineLen = min(lineLen, maxlen)
    lines = []
    thisline = ""
    def chunkword(word):
        if len(word)>lineLen:
            cut = min(lineLen-len(thisline), len(word)/2)
        else:
            cut = len(word)
        cut = max(1, cut)
        chunk = word[:cut]
        word = word[cut:]
        if word.strip():
            chunk += "-"
        return (chunk, word)
    for word in words:
        word = word+" "
        while word:
            (chunk, word) = chunkword(word)
            #print (thisline, chunk, word)
            #print "chunk", (chunk, word, thisline, lineLen)
            if len(chunk)+len(thisline)>lineLen:
                # emit thisline
                padding = (lineLen-len(thisline))/2
                thisline = " "*padding + thisline
                lines.append(thisline)
                # rechunk
                thisline = ""
                if chunk.endswith("-"):
                    chunk = chunk[:-1]
                word = (chunk+word).lstrip()
            else:
                # extend thisline
                thisline = thisline+chunk
            if len(lines)>=maxheight:
                #print "break on maxheight", (len(lines), maxheight)
                break
        if len(lines)>=maxheight:
            break
    #print "at termination", (thisline, chunk, word)
    if len(lines)<maxheight and thisline:
        lines.append(thisline)
    #print "lines", lines
    maxLineLen = max( map(len, lines) )
    height = len(lines)
    height = max( maxLineLen/2+1, height )
    toppadding = int((( height - len(lines) ) * dy)/2.0)
    maxy = (height*dy)
    starty = maxy-toppadding
    c = canvas.Canvas()
    c.setColor(37,27,163)
    c.setBackgroundColor(37,27,163)
    c.addFont("propell", "fonts/mlmfonts/propell.bdf")
    c.setFont("propell", 2.0, 1.3)
    count = 0
    y = starty
    x = dy/2
    testline = "*"*maxLineLen
    c.addText(0,0, testline)
    c.addText(0,maxy,testline)
    c.setColor(233,233,255)
    for line in lines:
        c.addText(x,y,line)
        y -= dy
    c.dumpToPNG(path)

def make_icon0(name, topath):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.setColor(10, 50, 10)
    c.setBackgroundColor(10, 50, 10)
    c.addFont("propell", "fonts/mlmfonts/propell.bdf")
    c.setFont("propell", 2.0, 1.3)
    count = 0
    y = 60
    c.addText(0,0,"*****")
    c.addText(0,60,"*****")
    c.setColor(99,100,200)
    for word in name.split():
        while word:
            chunk = word[:5]
            word = word[5:]
            c.addText(0,y,chunk)
            y -= 30
            count += 1
            if count>3: break
        if count>3: break
    for i in range(count,3):
        c.addText(0,y,"*")
        y -= 30
    c.dumpToPNG(topath)
    
# === tests
def test():
    install_demo("/tmp/demoize", "makedemo", "Make a Demo")
