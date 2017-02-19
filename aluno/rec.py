# -*- coding: utf-8 -*-

'''recorder.py
Provides WAV recording functionality via two approaches:
Blocking mode (record for a set duration):
'''
import sys
import os

import pyaudio
import wave
import time
import datetime
import threading

from array import array
from collections import deque

# http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
class SpeechDetection(threading.Thread):

	started = None
	stopped = None

	def __init__(self, q, t):
		threading.Thread.__init__(self)
		# or super(SpeechDetection, self).__init__()
		self.samples = q
		self.times = t
		self.event = threading.Event()

	def init_window(self, val):
		return deque([val], maxlen=6) 

	def stop(self):
		self.event.set()
		self.samples.clear()
		self.times.clear()

	def run(self):
		# Estimate initial silence
		initial_silence = []
		for i in xrange(10):
			while not len(self.samples):
				pass

			snd_data = array('h', self.samples.pop())
			initial_silence.append(max(snd_data))

		thresh = 600
		if int(max(initial_silence)) > thresh:
			thresh = int(max(initial_silence)) 

		del(initial_silence)

		print thresh
		if thresh > 5000:
			print 'muito alto'
			self.stop()
			return
	
		speech = self.init_window(False)
		detected = False
		while not self.event.is_set():
			while not len(self.samples):
				pass

			snd_data = array('h', self.samples.popleft())
			voiced = (int(max(snd_data)) > thresh)

			speech.append(voiced)
			if all(speech):
				detected = True
				break

		if detected:
			self.started = self.times.popleft()
		else:
			self.stop()
			return

		sys.stdout.write('started: %s\n' % self.started)

		silence = self.init_window(False)
		detected = False
		while not self.event.is_set():
			while not len(self.samples):
				pass

			snd_data = array('h', self.samples.popleft())
			unvoiced = (int(max(snd_data)) < thresh)

			silence.append(unvoiced)
			if all(silence):
				detected = True
				break

		if detected:
			self.stopped = self.times.popleft()

		sys.stdout.write('stopped: %s\n' % self.stopped)

		self.stop()
		return

# https://people.csail.mit.edu/hubert/pyaudio/docs/
# TODO: endianness!
def callback(in_data, frame_count, time_info, status):
	t.append(datetime.datetime.now())
	q.append(in_data)
	wavlock.acquire()
	wavfile.writeframes(in_data)
	wavlock.release()
	return (in_data, pyaudio.paContinue)

if __name__=='__main__':
	a = datetime.datetime.now()
	p = pyaudio.PyAudio()
	stream = p.open(format=pyaudio.paInt16,
				channels=1, rate=22050, frames_per_buffer=1024,
				input=True, start=False,
				stream_callback=callback)

	q = deque(maxlen=10)
	t = deque(maxlen=6)

	wavfile = wave.open('myvoice.wav', 'wb')
	wavfile.setnchannels(1)
	wavfile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
	wavfile.setframerate(22050)

	wavlock = threading.Lock()

	x = SpeechDetection(q, t)
	x.start()
	stream.start_stream()

	print '\n\n\n'
	x.join()
	b = datetime.datetime.now()

	while wavlock.locked():
		print 'topreso',
	print ''

	wavlock.acquire()
	wavfile.close()
	print 'passei'
	stream.close()
	stream.stop_stream()
	p.terminate()
	print 'passei'
	wavlock.release()

	print '0:', a
#	print 'delay:', (x.started-a).total_seconds()
#	print 'duration:', (x.stopped-x.started).total_seconds()

