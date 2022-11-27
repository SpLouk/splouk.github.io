#!/usr/bin/env python3
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import build

class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        super().on_any_event(event)
        try:
            print("Changes detected, rebuilding.")
            build.build_site()
            print("Rebuilt!")
        except Exception as err:
            print(f"{type(err)} {err}")

if __name__ == "__main__":
    path = "src/"

    handler = Handler()
    # Initialize Observer
    observer = Observer()
    observer.schedule(handler, path, recursive=True)

    # Start the observer
    observer.start()
    try:
        while True:
            # Set the thread sleep time
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
