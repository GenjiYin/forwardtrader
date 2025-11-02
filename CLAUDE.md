Traceback (most recent call last):
  File "d:\BaiduSyncdisk\2\天勤backtrader\test.py", line 71, in <module>
    cerebro.run()
  File "d:\BaiduSyncdisk\2\天勤backtrader\backtrader\cerebro.py", line 1132, in run
    runstrat = self.runstrategies(iterstrat)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "d:\BaiduSyncdisk\2\天勤backtrader\backtrader\cerebro.py", line 1303, in runstrategies
    self._runnext(runstrats)
  File "d:\BaiduSyncdisk\2\天勤backtrader\backtrader\cerebro.py", line 1562, in _runnext
    dt0 = min((d for i, d in enumerate(dts)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: min() iterable argument is empty