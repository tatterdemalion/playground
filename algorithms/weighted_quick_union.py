class WeightedQuickUnion(object):
    def __init__(self, n):
        self.n = n
        self.ids = list(range(n))
        self.sz = [1 for i in range(n)]

    def root(self, i):
        while i != self.ids[i]:
            self.ids[i] = self.ids[self.ids[i]]
            i = self.ids[i]
        return i

    def connected(self, p, q):
        return self.root(p) == self.root(q)

    def union(self, p, q):
        if not self.connected(p, q):
            i = self.root(p)
            j = self.root(q)
            if self.sz[i] < self.sz[j]:
                self.ids[i] = j
                self.sz[j] += self.sz[i]
            else:
                self.ids[j] = i
                self.sz[i] += self.sz[j]
        print(list(range(self.n)))
        print(self.ids)
        print(self.sz)
