import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import watchdog.events
import uploadLogs as ul
import main as m

c1 = []
c2 = []

class MyHandler(PatternMatchingEventHandler):
    patterns=["*access.log*"]
    def on_modified(self, event):
        global c1
        global c2
        flag = False
        c = []
        with open('/var/log/apache2/access.log', 'r') as content_file:
            content = content_file.read()
        if c1==[]:
            c1 = content.splitlines()
            return
        else:
            c2 = list(c1)
            c1 = content.splitlines()
        if len(c1) < len(c2):
            if len(c1) > 1:
                print("[Warning] Log modification suspected.")
                m.uploadthis("randomstring", c2)
                content_file.close()
                return
            c_len = len(c1)
        else:
            c_len = len(c2)
        if len(c2) >= 1 and len(c1) >= 1:
            for i in range(0,c_len):
                if c1[i] != c2[i]:
                    print("[Warning] Log modification suspected.")
                    flag = True
                    c.append(c2[i])
                    content_file.close()
        content_file.close()
        if flag:
            m.uploadthis("randomstring", c)
                
# print(event.src_path)


def handler():
    checkpath = '/var/log/apache2/'
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=checkpath, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except:
        print("[Warning] Watchdog died! Your logs are now vulnerable!")
        m.uploadthis("randomstring", c1)
        observer.stop()
    observer.join()

