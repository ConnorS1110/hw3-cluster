import testfile as test
from row import ROW
from cols import COLS
import utility as util
from collections.abc import Iterable
import copy

class DATA:

    def __init__(self, src):
        self.rows = []
        self.cols = None
        # self.halfCalls = 0
        fun = lambda x: self.add(x)
        if type(src) == str:
            test.readCSV(src, fun)
        else:
            map(fun, src or {})

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

    def clone(self, rows = None):
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
        data = self
        if rows:
            data.rows = rows
        return data

    def stats(self, what, cols, nPlaces, fun=None):
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

    def better(self, row1, row2):
        """
        Function:
            better
        Description:
            Determines if row1 dominates row2
        Input:
            self - current DATA instance
            row1 - First row to compare
            row2 - Second row to compare
        Output:
            True if row1 dominates row2
        """
        s1, s2, ys = 0, 0, self.cols.y
        for _, col in enumerate(ys):
            x = col.norm(row1.cells[col.at])
            y = col.norm(row2.cells[col.at])
            s1 -= col.w ** ((x - y) / len(ys))
            s2 -= col.w ** ((y - x) / len(ys))
        return (s1 / len(ys)) < (s2 / len(ys))

    def dist(self, row1, row2, cols = None):
        """
        Function:
            dist
        Description:
            Finds normalized distance between row1 and row2
        Input:
            self - current DATA instance
            row1 - First row
            row2 - Second row
            cols - cols to use as the data for distance
        Output:
            Normalized distance between row1 and row2
        """
        n, d = 0, 0
        for col in (cols or self.cols.x):
            n += 1
            d += col.dist(row1.cells[col.at], row2.cells[col.at]) ** util.args.p
        return (d / n) ** (1 / util.args.p)

    def around(self, row1, rows = None, cols = None):
        """
        Function:
            around
        Description:
            Sorts rows by distance to row1
        Input:
            self - current DATA instance
            row1 - Central row to do sorting by distance around
            rows - Rows to compare to distance from row1
            cols - cols to use as the data for sorting by distance to row1
        Output:
            Sorted list of rows by their distance to row1
        """
        if isinstance(rows, Iterable):
            iterable = rows
        else:
            iterable = self.rows

        rows_with_distance = [(row2, self.dist(row1, row2, cols)) for row2 in iterable]
        sorted_rows = sorted(rows_with_distance, key=lambda x: x[1])
        return [(row, dist) for row, dist in sorted_rows]
        # return sorted(rows, key=lambda row2: {'row': row2, 'dist': self.dist(row1, row2, cols)})

    def half(self, rows = None, cols = None, above = None):
        """
        Function:
            half
        Description:
            Splits data in half
        Input:
            self - current DATA instance
            rows - rows to split
            cols - cols to split
            above - previous point of split
        Output:
            left - list of rows to the left of split
            right - list of rows to the right of split
            A - far left point
            B - far right point
            mid - mid point where split occurs
            c - Distance between A and B
        """
        A, B, left, right, c, mid, some = None, None, None, None, None, None, None
        def project(row):
            return {'row': row, 'dist': util.cosine(dist(row, A), dist(row, B), c)[1]}
        def dist(row1, row2):
            return self.dist(row1, row2, cols)
        rows = rows or self.rows
        some = util.many(rows, util.args.Sample)
        A = above or util.any(some)
        B = self.around(A, some)[int((util.args.Far * len(rows)) // 1)][0]
        c = dist(A, B)
        left, right = [], []
        mapVAR = [project(row) for row in rows]
        sorted_rows = sorted(mapVAR, key=lambda x: x["dist"])
        for n, tmp in enumerate(sorted_rows):
            if n <= len(rows) // 2:
                left.append(tmp["row"])
                mid = tmp["row"]
            else:
                right.append(tmp["row"])
        # print("len of left" + str(len(left)))
        # print("len of right" + str(len(right)))
        return left, right, A, B, mid, c

    def cluster(self, rows = None, min = None, cols = None, above = None):
        """
        Function:
            cluster
        Description:
            Returns clustered rows by recursively splitting data
        Input:
            self - current DATA instance
            rows - rows to cluster
            cols - cols to cluster
            min - Determines when to stop splitting
            above - Previous point of split
        Output:
            Clustered rows
        """
        rows = rows if rows else self.rows
        min = min if min else len(rows) ** util.args.min
        cols = cols if cols else self.cols.x
        node = {"data": self.clone(rows)}

        if len(rows) > 2 * min:
            # print(len(self.half(rows, cols, above)))
            # self.halfCalls += 1
            # print("# of half calls: " + str(self.halfCalls))
            left, right, node["A"], node["B"], node["mid"], _ = self.half(rows, cols, above)
            node["left"] = self.cluster(left, min, cols, node["A"])
            node["right"] = self.cluster(right, min, cols, node["B"])
        return node

    def sway(self, rows, min, cols, above):
        """
        Function:
            sway
        Description:
            Finds the best half of the data by recursion
        Input:
            self - current DATA instance
            rows - rows to sway
            cols - cols to sway
            min - Determines when recursion stops
            above - Previous point of split
        Output:
            Swayed rows
        """
        rows = rows if rows else self.rows
        min = min if min else len(rows) ** util.args.min
        cols = cols if cols else self.cols.x
        node = {"data": self.clone(rows)}

        if len(rows) > 2 * min:
           left, right, node["A"], node["B"], node["mid"] = self.half(rows, cols, above)
           if self.better(node["B"], node["A"]):
               left, right, node["A"], node["B"] = right, left, node["B"], node["A"]
           node["left"] = self.sway(left,  min, cols, node["A"])

        return node
