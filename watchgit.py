#!/usr/bin/python3
# WatchGit version 0.0.1

import pyinotify
import argparse
import time
import git

class GitVersioning:
    def __init__(self, repository):
        self.remoteRepository=remoteUrl
        self.repository = git.Repo.init(repository)
    def fCreated(self, path):
        print("git add", path)
        self.repository.index.add(path)
    def fModified(self, path):
        print("git add", path)
        self.repository.index.add(path)
    def fRemoved(self, path):
        print("git rm", path)
        self.repository.index.remove(path)
    def fRenamed(self, src, dest):
        print("git mv", src, dest)
        self.repository.index.move([src,dest])
    def recordChanges(self):
        print("git commit -m", time.localtime())
        # self.repository.index.commit( .... )
    def remoteMigrate(self):
        print("git push")
        # self.repository.index.commit( .... )
        
class VersionHandler(pyinotify.ProcessEvent):
    def __init__(self, versioning):
        self.versioning = versioning

    def process_IN_CREATE(self, event):
        self.versioning.fCreated(event.pathname)

    def process_IN_DELETE(self, event):
        self.versioning.fRemoved(event.pathname)

    def process_IN_MODIFY(self, event):
        self.versioning.fModified(event.pathname)

    def process_IN_MOVED_FROM(self, event):
        self.move_from = event.pathname

    def process_IN_MOVED_TO(self, event):
        self.versioning.fRenamed(self.move_from, event.pathname)


# ---

def parse_app_arguments():
    def create_parser():
        descr  = "watchv version " + "0.0.1\n" 
        descr += " written by Leonard Siebeneicher"
        return argparse.ArgumentParser(description=descr) 
    def register_args(parser):
        parser.add_argument('repository', metavar='<local>')
        parser.add_argument('remote', metavar='<remote>')
        parser.add_argument('-V', '--versioning', dest='versioning', help='Chosie versioning system. Default will be GIT.')
    # --- parse_app_arguments ---
        
    parser = create_parser()
    register_args(parser)
    return parser.parse_args()

# ---
def main():
    args = parse_app_arguments()

    versioning = GitVersioning(args.repository, args.remote)
    handler = VersionHandler(versioning)

    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, handler)

    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO
    wdd = wm.add_watch(args.repository, mask, rec=True)

    notifier.loop()

if __name__ == '__main__':
    main()
