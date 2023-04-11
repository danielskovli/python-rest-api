'''Benchmarking tools'''

from typing import Any
from time import perf_counter


# Mostly from https://stackoverflow.com/questions/33987060/python-context-manager-that-measures-time
class catchtime:
	def __init__(self):
		self._finished = False
		self._start = 0.0
		self._end = 0.0

	def __enter__(self):
		self._start = perf_counter()
		return self

	def __exit__(self, *args: Any, **kwargs: Any):
		self._end = perf_counter()
		self._finished = True

	@property
	def duration(self):
		'''Retrieve in-progress or finished duration'''

		if self._finished:
			return self._end - self._start
		else:
			return perf_counter() - self._start

	time = duration