#!/usr/bin/python3
# WatchGit version 0.0.1

import os
from os import path
import time
import pyinotify
import git
import argparse


# 
# VCS Systems we can use to backup data
# 

# Echo for Debugging --- will be removed in future



class EchoCVS:
    def __init__(self, repository):
        self.repository = path.abspath(repository)
        self.change_occured = time.time()
        self.need_migrate=False

    def changed_since(self):
        return time.time()-self.change_occured

    def fCreated(self, path):
        print("Added:", path)
        self.change_occured=time.time()
        self.need_migrate=True
    
    def fModified(self, path):
        print("Modified:", path)
        self.change_occured=time.time()
        self.need_migrate=True
    
    def fRemoved(self, path):
        print("Removed:", path)
        self.change_occured=time.time()
        self.need_migrate=True
    
    def fRenamed(self, src, dest):
        print("Renamed:", src, dest)
        self.change_occured=time.time()
        self.need_migrate=True
        
    def remoteMigrate(self):
        print("Record Changes:", time.ctime())
        print("Migrating")
        self.need_migrate=False


class GitVersioning:
    def __init__(self, repository):
        self.repository = git.Repo(repository)
        self.change_occured=time.time()
        self.need_migrate=False
    
    def changed_since(self):
        return time.time()-self.change_occured

    def fCreated(self, p):
        print("File created:", p)
        self.repository.index.add([p])
        self.change_occured=time.time()
        self.need_migrate=True
    
    def fModified(self, p):
        print("File modified:", p)
        self.repository.index.add([p])
        self.change_occured=time.time()
        self.need_migrate=True
    
    def fRemoved(self, p):
        print("File removed:", p)
        self.repository.index.remove([p])
        self.change_occured=time.time()
        self.need_migrate=True
    
    def fRenamed(self, src, dest):
        print(src, "renamed to", dest)
        self.repository.index.remove([src])
        self.repository.index.add([dest])
        self.change_occured=time.time()
        self.need_migrate=True
    
    def remoteMigrate(self):
        print("Migrating changes")
        self.repository.index.commit( time.ctime() )
        # o = self.repository.remotes['origin']
        # o.push()
        self.need_migrate=False
        
def chose_version_handler(args):
    v = args.vcs
    print("Repository: ", args.repository)
    if v == 'git':
        print("Using GIT")
        return GitVersioning(args.repository)
    elif v == 'echo':
        print("Using ECHO")
        return EchoCVS(args.repository)
    else:
        sys.exit("Versioning not supportet: " + v)


# 
# We derive VcsHandler from pyinotify.ProcessEvend.
# 

class VcsHandler(pyinotify.ProcessEvent):
    def __init__(self, vcs):
        self.vcs = vcs
        self.change_occured=time.time()
        
    def process_IN_CREATE(self, event):
        self.vcs.fCreated(event.pathname)

    def process_IN_DELETE(self, event):
        self.vcs.fRemoved(event.pathname)

    def process_IN_MODIFY(self, event):
        self.vcs.fModified(event.pathname)

    def process_IN_MOVED_FROM(self, event):
        self.move_from = event.pathname

    def process_IN_MOVED_TO(self, event):
        self.vcs.fRenamed(self.move_from, event.pathname)

#
# Argument Parsing comes here
#

def parse_app_arguments():
    def create_parser():
        descr  = "watchv version " + "0.0.1\n" 
        descr += " written by Leonard Siebeneicher"
        return argparse.ArgumentParser(description=descr) 
    def register_args(parser):
        parser.add_argument('repository', metavar='<local>')
        # parser.add_argument('remote', metavar='<remote>')
        parser.add_argument('-V', '--vcs', dest='vcs', default='git',
                help='Chosie vcs system. Default will be GIT. Possible Values: [git, echo]')
        parser.add_argument('-p', '--period', dest='period', type=int, default=15,
                help='After <period> amount of minutes passed since last change, watchgit will do a push. Default to 15 minutes')

    # After defining some subroutines, lets perform argument parsing        
    parser = create_parser()
    register_args(parser)
    return parser.parse_args()

# 
# The Main routine
# 

def main():
    def init_pyinotify(args, watchmanager):        
        watch = watchmanager.add_watch(
            args.repository, 
            pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | 
            pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO, 
            rec=True,
            exclude_filter=pyinotify.ExcludeFilter(
                [ '.*(\.git)'
                ])
            )

        notifier = pyinotify.ThreadedNotifier(watchmanager, handler)
        notifier.start()
        #watchmanager.rm_watch(list(watch.values()))
        
        return watch, notifier

    def app_loop(args, V, notifier):
        minute_period = args.period*60 
        while(True):
            # wait 30 secs
            time.sleep(30) 
            
            if ( V.changed_since() > minute_period and V.need_migrate):
                V.remoteMigrate()
                
        notifier.stop()

    # ---
    args = parse_app_arguments()
    V = chose_version_handler(args)
    handler = VcsHandler( V )
    watchmanager = pyinotify.WatchManager()
    
    watch, notifier = init_pyinotify(args, watchmanager)
    app_loop(args, V, notifier)


if __name__ == '__main__':
    main()
