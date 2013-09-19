import os
import settings
import models.node as node
import datetime

def get_images(self, time=None, frm=None, to=None):
        da_files = []
        for root, dirs, files in os.walk(settings.TIMELAPSE_PATH):
            for name in files:
                if name.startswith('.') == False:
                    f = os.path.join(root, name)
                    size = os.path.getsize(f)
                    if size > 200:
                        mod = mod_date(f)
                        filename = "%s%s" % (settings.TIMELAPSE_URL, name)
                        obj = dict(mod=mod, file=filename)
                        if (frm and to) and mod >= frm and mod < to: 
                            da_files.append(obj)
                        elif time and mod >= time:
                            da_files.append(obj)

        da_files.sort()
        return da_files

def get_data(self, node_id, type, frm=None, to=None, images=False):
    time = datetime.datetime.utcnow()
    step = 1
    if type == 'hour':            
        time = datetime.datetime.utcnow()-datetime.timedelta(hours=1)
    if type == 'day':
        step = 6
        time = datetime.datetime.utcnow()-datetime.timedelta(hours=24)
    if type == 'week':
        step = 18
        time = datetime.datetime.utcnow()-datetime.timedelta(days=7)
    if type == 'month':
        step = 36
        time = datetime.datetime.utcnow()-datetime.timedelta(days=30)        
    q = dict(
        node=node_id, 
        timestamp={'$gte':time}
    )
    if type == 'custom':
        step = 18
        frm = datetime.datetime.strptime(frm, "%m-%d-%Y")
        to = datetime.datetime.strptime(to, "%m-%d-%Y")
        q['timestamp'] = {'$gte':frm, '$lt':to}


    if images: images = get_images(time, frm, to)
    self.logger.debug("Query: %s" % q)        
    res = node.SensorValue.find(q, as_dict=True, fields={'timestamp':1,'sensor':1,'value':1})
    res.batch_size(10000)
    res = [res[i] for i in xrange(0, res.count(), step)]
    return res, images