from boto.s3.connection import S3Connection
from boto.s3.key import Key
from urllib import urlretrieve
import urllib
import time
import gevent
import util
import settings

class DownloadImage(object):

    def __init__(self, id, url, path, period, s3=False, cb=False):
        self.path = path
        self.url = url
        self.id = id
        self.running = True
        self.secs = period
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.s3 = s3
        self.cb = cb
        gevent.spawn(self.run)
    
    def run(self):
        while self.running:
            now = int(time.time())
            self.logger.info("Loading: %s" % self.id)
            start = now            
            if self.s3:
                filename = self.to_s3()
                if filename and self.cb: self.cb(filename, self.id)
            else:
                try:
                    filename = "%s%s.jpg" % (self.id, str(now))
                    name = self.path+filename
                    self.logger.info("Downloading: %s" % name)
                    urlretrieve(self.url, name)
		    if filename and self.cb: self.cb(filename, self.id)
                except IOError as er:
                    self.logger.exception(er)
            gevent.sleep(self.secs)

    def to_s3(self):
        now = int(time.time())
        filename = "%s/image%s.jpeg" % (self.id, str(now))
        self.logger.warn("URL: %s" % self.url)
        f = urllib.urlopen(self.url)
        st = f.read()
        f.close()
        if len(st) > 1000:
            return self.upload(st, filename)
        return False            
    
    def upload(self, data, filename):
        conn = S3Connection(settings.AWS_KEY, settings.AWS_SECRET)
        bucket = conn.create_bucket(settings.S3_BUCKET)
        obj = Key(bucket)
        obj.key = filename
        obj.set_metadata("Content-Type", 'image/jpeg')    
        obj.set_contents_from_string(data)
        obj.set_acl("public-read")
        obj.close()
        conn.close()
        return filename


