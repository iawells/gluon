import threading
import Queue
import json
from gluon.common.particleGenerator.generator import getDataBaseGeneratorInstance as getDBGen
from gluon.db import api as dbapi
from oslo_log import log as logging
import etcd

LOG = logging.getLogger(__name__)

service = "net-l3vpn"
source = "proton"
port = 2379

class MyData:
    pass

SyncData = MyData()
SyncData.sync_thread_running = False
SyncData.sync_queue = Queue.Queue()


class SyncThread(threading.Thread):
    """ A worker thread that takes takes commands to
        update etcd with table changes.
    """
    def __init__(self, input_q):
        super(SyncThread, self).__init__()
        self.input_q = input_q
        self.db_instance = dbapi.get_instance()
        self.etcd_client = etcd.Client(port=port)
        LOG.info("SyncThread starting")

    def proc_sync_msg(self, msg):
        try:
            obj_key = "_".join(msg["key"].split())  # Get rid of spaces
            etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format(service, source, msg["table"], obj_key)
            if msg["operation"] == "update":
                table_class = getDBGen().get_table_class(msg["table"])
                data = self.db_instance.get_by_primary_key(table_class, msg["key"])
                values = data.as_dict()
                d = {}
                for key in values.iterkeys():
                    d[key] = str(values[key])
                json_str = json.dumps(d)
                self.etcd_client.write(etcd_key, json_str)
            elif msg["operation"] == "delete":
                self.etcd_client.delete(etcd_key)
            else:
                LOG.error("Unkown operation in msg %s" % (msg["operation"]))
        except Exception as e:
            print(e.__doc__)
            print(e.message)
            LOG.error("Error writing to etcd %s, %s" % (e.__doc__, e.message))
            raise ValueError

    def run(self):
        while 1:
            try:
                msg = self.input_q.get(True, 10.0)
                LOG.info("SyncThread: received message %s " % msg)
                self.proc_sync_msg(msg)
            except Queue.Empty:
                LOG.debug("SyncThread: Queue timeout")
            except ValueError:
                LOG.error("Error processing sync message")
                break
        LOG.error("SyncThread exiting")
        SyncData.sync_thread_running = False


def start_sync_thread():
    SyncData.sync_thread = SyncThread(SyncData.sync_queue)
    SyncData.sync_thread_running = True
    SyncData.sync_thread.start()
