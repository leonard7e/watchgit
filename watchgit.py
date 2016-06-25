#!/usr/bin/python3
# WatchGit version 0.0.1

import time
import pyinotify
import git
import argparse


# 
# VCS Systems we can use to backup data
# 

class EchoCVS:
    def __init__(self, repository):
        self.repository = git.Repo(repository)
    def fCreated(self, path):
        print("Added:", path)
    def fModified(self, path):
        print("Modified:", path)
    def fRemoved(self, path):
        print("Removed:", path)
    def fRenamed(self, src, dest):
        print("Renamed:", src, dest)
    def recordChanges(self):
        print("Record Changes:", time.localtime())
    def remoteMigrate(self):
        print("Migrating")


class GitVersioning:
    def __init__(self, repository):
        self.remoteRepository=remoteUrl
        self.repository = git.Repo(repository)
    def fCreated(self, path):
        self.repository.index.add(path)
    def fModified(self, path):
        self.repository.index.add(path)
    def fRemoved(self, path):
        self.repository.index.remove(path)
    def fRenamed(self, src, dest):
        self.repository.index.move([src,dest])
    def recordChanges(self):
        print("git commit -m", time.localtime())
        # self.repository.index.commit( .... )
    def remoteMigrate(self):
        print("git push")
        # self.repository.index.commit( .... )
        
def chose_version_handler(args):
    v = args.vcs
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

    # After defining some subroutines, lets perform argument parsing        
    parser = create_parser()
    register_args(parser)
    return parser.parse_args()

# 
# The Main routine
# 

def main():
    def init_pyinotify(args, watchmanager):        
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO
        watch = watchmanager.add_watch(args.repository, mask, rec=True )

        notifier = pyinotify.ThreadedNotifier(watchmanager, handler)
        notifier.start()
        
        # watchmanager.rm_watch(watch.values())
        return watch, notifier

    def app_loop(args, V, notifier):
        while(True):
            time.sleep(60*1) # 60*15
            # test whether we need to commit changes
            if (True): 
                V.recordChanges()
                V.remoteMigrate()
                
        notifier.stop()

    # TODO: Versionierung aus ArgumentParser beziehen.
    args = parse_app_arguments()
    V = chose_version_handler(args)
    handler = VcsHandler( V )
    watchmanager = pyinotify.WatchManager()
    
    watch, notifier = init_pyinotify(args, watchmanager)
    app_loop(args, V, notifier)




if __name__ == '__main__':
    main()


# TODO
# - test whether we need to commit changes
