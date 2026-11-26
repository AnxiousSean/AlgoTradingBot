import backtrader as bt


class MicroProbe(bt.Strategy):
    params = (("demo", 1),)

    def __init__(self):
        self.count = 0
        print("PROBE|micro init ok")

    def next(self):
        self.count += 1
        if self.count == 1:
            print("PROBE|micro first bar", self.data.datetime.datetime(0), self.data.close[0])

    def stop(self):
        print("PROBE|micro done bars=" + str(self.count) + " value=" + str(self.broker.getvalue()))
