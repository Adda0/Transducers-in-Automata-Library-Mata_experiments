from math import ceil, log2


class Bitvector:
    def __init__(self, domain: set, nondet_level: int) -> None:
        self.nondet_level = nondet_level
        self.nondet_prefix_len = ceil(log2(self.nondet_level))
        self.domain_size = len(domain)
        self.vector_len = ceil(log2(self.domain_size))
        self.mapping = dict()

        i = 0
        EPSILON = "4294967295"
        if EPSILON in domain:
            self.mapping[EPSILON] = self.int2bin(i, self.vector_len)
            i += 1
        for val in sorted(domain.difference({EPSILON})):
                self.mapping[val] = self.int2bin(i, self.vector_len)
                i += 1

    def int2bin(self, val: int, size: int) -> str:
        if size == 0:
            return ""
        return bin(val)[2:].zfill(size)

    def translate(self, val, prefix_val=0) -> str:
        return self.int2bin(prefix_val, self.nondet_prefix_len) + self.mapping[val]


if __name__ == "__main__":
    import sys
    domain = set(sys.argv[1].split(","))
    bitvector = Bitvector(domain)

    for arg in sys.argv[2:]:
        print(f"{arg} -> {bitvector.translate(arg)}")
