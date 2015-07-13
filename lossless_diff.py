#!/usr/bin/env python2.7

import struct, sys, wave

class Audio:
    def __init__(self, wav_file, new_params = None):
        if new_params:
            self.wav = wave.open(wav_file, 'w')
            self.wav.setparams(new_params)
        else:
            self.wav = wave.open(wav_file, 'r')
        (self.nchannels, self.sampwidth, self.framerate, self.nframes, self.comptype, self.compname) = self.wav.getparams()
        (self.max, self.sum) = [0] * 2
        struct_code = {1:'b', 2:'h', 4:'i', 8:'q'}[self.sampwidth]
        self.fmt = "<" + struct_code * self.nchannels # little endian
        assert struct.calcsize(self.fmt) == self.nchannels * self.sampwidth
        self.peak = float(2 ** (self.sampwidth * 8)) / 2 - 1

        if False:
            for i in range(self.nframes):
                self.process_frame()
            print self.stats()

    def read_frame(self):
        octets = self.wav.readframes(1)
        if not octets:
            return None
        assert len(octets) == self.nchannels * self.sampwidth
        channels = struct.unpack(self.fmt, octets)
        for sample in channels:
            self.process_sample(sample)
        return channels

    def write_frame(self, channels):
        octets = struct.pack(self.fmt, *channels) # allows variable number of channels
        for sample in channels:
            self.process_sample(sample)
        self.wav.writeframes(octets)

    def process_sample(self, sample):
        if sample > self.max:
            self.max = sample
        self.sum += abs(sample)

    def stats(self):
        avg = float(self.sum) / (self.nframes * self.nchannels)
        return "max %.1f %%, average %.1f %%" % (100 * self.max / self.peak, 100 * avg / self.peak)

def main():
    lossless = Audio(sys.argv[1])
    lossy = Audio(sys.argv[2])
    assert(lossy.wav.getparams() == lossless.wav.getparams())
    diff = Audio(sys.argv[3], lossless.wav.getparams())
    while True:
        a = lossless.read_frame()
        b = lossy.read_frame()
        if not a and not b:
            break
        channels = []
        for i in range(len(a)):
            d = a[i] - b[i]
            channels.append(d)
        # print a, b, channels
        diff.write_frame(channels)

main()
