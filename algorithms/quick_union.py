class QuickUnion(object):
    ids = list(range(10))

    def root(self, i):
        while i != self.ids[i]:
            i = self.ids[i]
        return i

    def connected(self, p, q):
        return self.root(p) == self.root(q)

    def union(self, p, q):
        i = self.root(p)
        j = self.root(q)
        self.ids[i] = j
