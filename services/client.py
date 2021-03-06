__author__ = 'tanel'

import argparse
from ws4py.client.threadedclient import WebSocketClient
import time
import threading
import sys
import urllib
import queue as Queue
import json
import time
import os
import wave


def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate


class MyClient(WebSocketClient):

    def __init__(self, audiofile, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super(MyClient, self).__init__(
            url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.audiofile = audiofile
        self.byterate = byterate
        self.final_hyp_queue = Queue.Queue()
        self.final_result = []
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename

    @rate_limited(4)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        print("Socket opened!")

        def send_data_to_ws():
            # if self.send_adaptation_state_filename is not None:
            #     print >> sys.stderr, "Sending adaptation state from %s" % self.send_adaptation_state_filename
            #     try:
            #         adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
            #         self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
            #     except:
            #         e = sys.exc_info()[0]
            #         print >> sys.stderr, "Failed to send adaptation state: ",  e

            # with open(self.audiofile, 'rb') as audiostream:
            if(type(self.audiofile) == type('')):
                self.audiofile = open(self.audiofile, 'rb')

            with self.audiofile as audiostream:
                block = audiostream.read(self.byterate//4)
                while(block != b''):
                    self.send_data(block)
                    block = audiostream.read(self.byterate//4)

            print("Audio sent, now sending EOS", file=sys.stderr)
            self.send("EOS")
            self.audiofile.close()

        t = threading.Thread(target=send_data_to_ws)
        t.start()
        # send_data_to_ws()

    def received_message(self, m):
        response = json.loads(str(m))
        # print(response)
        if response['status'] == 0:
            if 'result' in response:
                # print('hello')
                if response['result']['final']:
                    self.final_hyps += [res for res in response['result']
                                        ['hypotheses']]
                    # print('final_hyps', self.final_hyps, file=sys.stderr)
                # else:
                #     print_trans = trans.replace("\n", "\\n")
                #     if len(print_trans) > 80:
                #         print_trans = "... %s" % print_trans[-76:]
                #     print('\r%s' % print_trans, file=sys.stderr)

            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print >> sys.stderr, "Saving adaptation state to %s" % self.save_adaptation_state_filename
                    with open(self.save_adaptation_state_filename, "w") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            print("Received error from server (status %d)" %
                  response['status'], file=sys.stderr)

            if 'message' in response:
                print("Error message: {}".format(
                    response['message']), file=sys.stderr)

    def get_full_hyp(self, timeout=5):
        print('get result')
        result = []
        try:
            result = self.final_hyp_queue.get(timeout=timeout)
        except Exception as E:
            print('empty')
            pass
        # print('print from get_full_hyp', [result] + list(self.final_hyp_queue.queue))
        if(result != []):
            return [result] + list(self.final_hyp_queue.queue)
        else:
            return list(self.final_hyp_queue.queue)
        # return self.final_result
        # print('full_hyp', self.final_hyps)
        # return self.final_hyps

    def closed(self, code, reason=None):
        print("Websocket closed() called")
        #print >> sys.stderr
        # self.final_hyp_queue.put(self.final_hyps)
        # print(self.final_hyps)
        for hyp in self.final_hyps:
            self.final_hyp_queue.put(hyp)

        # print("KUY")
        # return self.get_full_hyp()
        # self.final_result = self.final_hyps
        # print('final res:', self.final_result)


def main():

    parser = argparse.ArgumentParser(
        description='Command line client for kaldigstserver')
    parser.add_argument('-u', '--uri', default="ws://localhost:8888/client/ws/speech",
                        dest="uri", help="Server websocket URI")
    parser.add_argument('-r', '--rate', default=32000, dest="rate", type=int,
                        help="Rate in bytes/sec at which audio should be sent to the server. NB! For raw 16-bit audio it must be 2*samplerate!")
    parser.add_argument('--save-adaptation-state',
                        help="Save adaptation state to file")
    parser.add_argument('--send-adaptation-state',
                        help="Send adaptation state from file")
    parser.add_argument('--content-type', default='',
                        help="Use the specified content type (empty by default, for raw files the default is  audio/x-raw, layout=(string)interleaved, rate=(int)<rate>, format=(string)S16LE, channels=(int)1")
    parser.add_argument('audiofile', help="Audio file to be sent to the server",
                        type=argparse.FileType('rb'), default=sys.stdin)
    args = parser.parse_args()

    content_type = args.content_type
    if content_type == '' and args.audiofile.name.endswith(".raw"):
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" % (
            args.rate/2)

    ws = MyClient(args.audiofile, args.uri + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])), byterate=args.rate,
                  save_adaptation_state_filename=args.save_adaptation_state, send_adaptation_state_filename=args.send_adaptation_state)
    ws.connect()
    result = ws.get_full_hyp()
    # print result.encode('utf-8')
    print(result)


if __name__ == "__main__":
    main()
