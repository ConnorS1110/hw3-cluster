import testfile as test
from row import ROW
from cols import COLS

class DATA:
    def __init__(self, src):
        self.rows = []
        self.cols = None
        fun = lambda x: self.add(x)
        if type(src) == str:
            test.readCSV(src, fun)
        else:
            map(src or {}, fun)

    def add(self, t):
        """
        Function:
            add
        Description:
            Adds the data to rows and cols, or makes a COLS if there aren't any columns stored yet
        Input:
            self - current DATA instance
            t - data to be added
        Output:
            None
        """
        if self.cols:
            t = t.cells if hasattr(t, "cells") else ROW(t)
            self.rows.append(t)
            self.cols.add(t)
        else:
            self.cols = COLS(t)

    def clone(self, init, x):
        """
        Function:
            clone
        Description:
            Creates a clone of the DATA object and returns it
        Input:
            self - current DATA instance
            init - init counter
            x - data to be cloned
        Output:
            data - Clone of DATA object
        """
        data = DATA({self.cols.names})
        map(init or {}, data.add(x))
        return data

    def stats(self, what, cols, nPlaces):
        """
        Function:
            stats
        Description:
            Gets a given statistic and returns the rounded answer
        Input:
            self - current DATA instance
            what - statistic to be returned
            cols - cols to use as the data for statistic
            nPlaces - # of decimal places stat is rounded to
        Output:
            map of cols y position and anonymous function that calculates the rounded stat
        """
        def fun(col):
            mid = getattr(col, what or "mid")
            rounded = round(float(mid()), nPlaces)
            return (rounded, col.txt)
        return test.kap(cols or self.cols.y, fun)
