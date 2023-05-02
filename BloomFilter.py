import math
import mmh3

class BloomFilter:
    def __init__(self, capacity, false_positive_rate):
        self.capacity = capacity
        self.false_positive_rate = false_positive_rate
        self.num_bits = int(-capacity * math.log(false_positive_rate) / (math.log(2)**2))
        self.num_hashes = int(self.num_bits * math.log(2) / capacity)
        self.bit_array = [False] * self.num_bits
        
    def add(self, item):
        for i in range(self.num_hashes):
            index = mmh3.hash(item, i) % self.num_bits
            self.bit_array[index] = True
            
    def __contains__(self, item):
        for i in range(self.num_hashes):
            index = mmh3.hash(item, i) % self.num_bits
            if not self.bit_array[index]:
                return False
        return True