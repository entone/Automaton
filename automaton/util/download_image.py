from urllib import urlretrieve
import time
import gevent
import util

class DownloadImage(object):

    def __init__(self, name, url, path, period):
        self.path = path
        self.url = url
        self.name = name
        self.running = True
        self.secs = period
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        gevent.spawn(self.run)
    
    def run(self):
        while self.running:
            now = int(time.time())
            self.logger.info("Loading: %s" % self.name)
            start = now
            name = self.path+self.name+str(now)+'.jpg'
            self.logger.info("Downloading: %s" % name)
            try:
                urlretrieve(self.url, name)
            except IOError as er:
                print er
            gevent.sleep(self.secs)