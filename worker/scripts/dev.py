#!/usr/bin/env python3
import os
import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class CeleryRestartHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_restart = 0

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return

        # Avoid rapid restarts
        current_time = time.time()
        if current_time - self.last_restart < 2:
            return

        self.last_restart = current_time
        print(f"📝 File changed: {os.path.basename(event.src_path)}")
        self.restart_callback()


class DevCeleryWorker:
    def __init__(self):
        self.process = None
        self.observer = None

    def start_celery(self):
        if self.process:
            self.stop_celery()

        print("🚀 Starting Celery worker...")
        cmd = ["celery", "-A", "tasks", "worker", "--loglevel=info", "--pool=solo"]
        self.process = subprocess.Popen(cmd)

    def stop_celery(self):
        if self.process:
            print("🛑 Stopping Celery worker...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None

    def restart_celery(self):
        print("🔄 Restarting Celery worker...")
        self.start_celery()

    def run(self):
        try:
            self.start_celery()

            # Setup file watcher
            event_handler = CeleryRestartHandler(self.restart_celery)
            self.observer = Observer()
            self.observer.schedule(event_handler, ".", recursive=True)
            self.observer.start()

            print("👀 Watching for file changes... Press Ctrl+C to stop")

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()
            self.stop_celery()


if __name__ == "__main__":
    worker = DevCeleryWorker()
    worker.run()
