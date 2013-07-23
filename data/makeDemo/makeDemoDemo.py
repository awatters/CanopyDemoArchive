#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Install a canopy demo.
"""

# Imports:
from traits.api \
    import HasTraits, Directory, Str, Float, Button

from traitsui.api \
    import Item, Group, View

import os.path
import re

import demoize

INFO ="""DEMO INSTALLER

Please specify
   - The identifier to use for the demo.
   - The readable name to use for the demo.
   - The directory location for the demo source.
   - The tags for classifying the demo.
The demo will be installed to your local Canopy demo list.
"""

# Define the demo class:
class DirectoryEditorDemo ( HasTraits ):
    """ Define the main DirectoryEditor demo class. """

    demo_id = Str("")
    demo_id_regex = re.compile('[a-zA-Z0-9]+')

    def _demo_id_changed(self, new):
        self.error = "demo_id: "+new
        self.check_demo_id(new)

    def check_demo_id(self, value):
        if len(value)<4:
            self.error = 'Demo id should be longer than 4 letters.'
            return None
        match = self.demo_id_regex.match(value)
        if match is None:
            self.error = 'Demo id should have one or more letters and numbers.'
            return None
        elif match.end()<len(value):
            self.error = 'Demo id should contain only letters or numbers.'
            return None
        return value

    demo_name = Str("")

    def _demo_name_changed(self, new):
        self.error = "demo_name: "+new
        self.check_demo_name(new)

    def check_demo_name(self, value):
        if len(value)<4:
            self.error = 'Name should be more than 3 letters.'
            return None
        return value

    demo_info = Str(INFO)

    demo_tags = Str("General")

    def _demo_tags_changed(self, new):
        self.error = "demo_tags: "+new
        self.check_demo_tags(new)
    
    def check_demo_tags(self, value):
        tags = []
        for s in value.split():
            for t in s.split(','):
                tags.append(t)
        for t in tags:
            if len(t)<2:
                self.error = \
                    'Tag names should be more than 1 letters long: '+repr(t)
                return None
        return tags

    demo_version = Float(1)

    dir_name = Directory

    def _dir_name_changed(self, new):
        self.error = "dir_name: "+new
        self.check_dir_name(new)

    def check_dir_name(self, value):
        if not os.path.isdir(value):
            self.error = 'Directory not found.'
        return value

    error = Str()

    check = Button('Check')

    def _check_fired(self):
        #print dir(self.check)
        self.error = "Checking..."
        self.check_input()

    def check_input(self):
        ok = False
        dir_name = self.check_dir_name(self.dir_name)
        demo_tags = self.check_demo_tags(self.demo_tags)
        demo_name = self.check_demo_name(self.demo_name)
        demo_id = self.check_demo_id(self.demo_id)
        version = self.demo_version
        if dir_name and demo_tags and demo_name and demo_id:
            self.error = "Parameters ok..."
            analysis = demoize.analyze(dir_name)
            filenames = sorted(analysis.keys())
            report = []
            icon_found = False
            for fn in filenames:
                (p,cat,is_dir) = analysis[fn]
                if is_dir:
                    line = "%s (zipped %s directory)" % (fn,cat)
                else:
                    line = "%s (%s)" % (fn,cat)
                report.append(line)
                if cat=="icon":
                    icon_found = True
            if not icon_found:
                report.append("WARNING: Icon file will be generated.")
            demo_script_name = demo_id+"Demo.py"
            if not demo_script_name in filenames:
                report.append("WARNING: No %s default script found" %
                              repr(demo_script_name))
            self.error = "\n".join(report)
            ok = True
        return (ok, dir_name, demo_tags, demo_name, demo_id, version)

    install = Button('Install')

    def _install_fired(self):
        self.error = 'Installing...'
        self.install_demo()

    def install_demo(self):
        (ok, dir_name, demo_tags, demo_name, demo_id, version) =\
            self.check_input()
        err = self.error
        if ok:
            demoize.install_demo(
                from_directory=dir_name,
                demo_id=demo_id,
                demo_name=demo_name,
                tags=demo_tags,
                version=version)
            self.error = err+"\n\nInstalled. Reload demo list to test."
        else:
            self.error = err+"\n\nPlease correct data problems."
    
    dir_group = Group(
        Item( 'demo_info', show_label=False, style='readonly' ),
        Item( 'demo_name', label='Name' ),
        Item( 'demo_id', label='Identifier' ),
        Item( 'demo_tags', label='Tags' ),
        Item( 'dir_name', style = 'simple',   label = 'Directory' ),
        Item( 'error', style='readonly', label='Message'),
        Item( 'check', show_label=False ),
        Item( 'install', show_label=False ),
    )

    # Demo view:
    view = View(
        dir_group,
        title     = 'Install Demo',
        buttons   = ['OK'],
        resizable = True
    )

# Create the demo:
demo = DirectoryEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    print "dir", demo.dir_name


