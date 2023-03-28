# Name: Michael Vuong
# OSU Email: vuongmi@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: 6 - HashMap Implementation
# Due Date: 3/17/23
# Description: This is an implementation of the HashMap class. The class utilizes a dynamic array to store the hash table and implements open addressing with quadratic probing for collision resolution. Key/value pairs are stored as objects
# within the dynamic array. The following methods are included in this class and a docstring is provided for each method: put(), get(), remove(), contains_key(), empty_buckets(), resize_table(), table_load(), get_keys(), __iter__(), and __next__().

from a6_include import (DynamicArray, DynamicArrayException, HashEntry,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number to find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        """
        This method updates the key/value pair in the hash map. If the given key already exists in the hash map, its associated value is replaced with the new value. if the given key is not in the hash map, a new key/value pair is added.
        Starts by checking the load factor if it follows the properties of a hash map and resize if it does not. Then computes the hash index for the key_value pair. It will traverse the dynamic array until an open spot is found for the value. 
        The traversal utilizes quadratic probing to find open spots. 
        """
        if self.table_load() >= 0.5:
            self.resize_table(self._capacity * 2)
        hash = self._hash_function(key)
        start_index = hash % self._capacity 
        index = start_index
        quadratic_coefficient = 1
        while self._buckets[index] is not None: #if the index has a value
            if self._buckets[index].is_tombstone:
                break
            elif self._buckets[index].key == key: #switch values if the key matches the value as it is traversing
                self._buckets[index].value = value
                return
            else:
                index = (start_index + (quadratic_coefficient**2)) % self._capacity 
                quadratic_coefficient += 1
        new_hash = HashEntry(key, value)
        self._buckets[index] = new_hash
        self._size += 1
        
    def table_load(self) -> float:
        """
        This method returns the current hash table load factor which is the current number of elements divided by the capacity.
        """
        return float(self._size) / float(self._capacity)

    def empty_buckets(self) -> int:
        """
        This method traverses the dynamic array and finds any value that is none or is a tombstone. Then returns that count, which represents the number of empty "buckets"
        """
        count = 0
        for index in range(self._capacity):        
                if self._buckets[index] is None or self._buckets[index].is_tombstone:
                    count += 1
        return count
    
    def resize_table(self, new_capacity: int) -> None:      
        """
        This method changes the capacity of the internal hash table. All existing key/value pairs are moved to a new dynamic array with the correct capacity and rehashed. First checks if new_capacity is not less than the current
        number of elements in the hash map; if so, the method does nothing. Then checks if the new_capacity is valid by making it a prime number if it is not. A new dynamic array is created with the appropriate allocation of capacity.
        Then will begin traversal of the original dynamic array and takes each key/value to use for the put() method. Tombstone values are ignored and left in the original dynamic array, Once all values are successfully copied over, 
        the new dynamic array will become self._buckets.
        """
        if new_capacity < self._size:
            return
        if not self._is_prime(new_capacity):
            new_capacity = self._next_prime(new_capacity)
        new_buckets = DynamicArray()
        for spaces in range(new_capacity):
            new_buckets.append(None)
        old_buckets = self._buckets
        self._buckets = new_buckets
        old_capacity = self._capacity
        self._capacity = new_capacity
        self._size = 0
        for i in range(old_capacity): 
            if old_buckets[i] is not None and not old_buckets[i].is_tombstone:  #for every value in self._buckets, as long as it is not None and not a tombstone
                key, value = old_buckets[i].key, old_buckets[i].value
                self.put(key, value)

    def get(self, key: str):
        """
        This method returns the value associated with the given key. If the key is not in the hash map, the method returns None. Follows the same quadratic probing as the put() method to locate the value easier.
        """
        new_hash = self._hash_function(key)
        start_index = new_hash % self._capacity
        index = start_index
        quadratic_coefficient = 1
        while self._buckets[index] is not None:
            if self._buckets[index].key == key and not self._buckets[index].is_tombstone:
                return self._buckets[index].value
            index = (start_index + (quadratic_coefficient ** 2)) % self._capacity
            quadratic_coefficient += 1
        return None
        
        

    def contains_key(self, key: str) -> bool:
        """
        This method returns True if the given key is not in the hash map. Otherwise it returns false. Utilizes the get() method to find the value. If the value is found, then this method will return true.
        """
        if self.get(key) is not None:
            return True
        return False

    def remove(self, key: str) -> None:
        """
        This method removes the given key and its associated value from the hash map. If the key is not in the hash map, the method does nothing. Utilizes quadratic probing to locate the value. Self._size is decremented by 1.
        """
        new_hash = self._hash_function(key)
        start_index = new_hash % self._capacity
        index = start_index
        quadratic_coefficient = 1
        while self._buckets[index] is not None:
            if self._buckets[index].key == key and not self._buckets[index].is_tombstone:
                self._buckets[index].is_tombstone = True
                self._size -= 1
                return
            index = (start_index + (quadratic_coefficient ** 2)) % self._capacity
            quadratic_coefficient += 1

    def clear(self) -> None:
        """
        This method clears all the contents of the hash map. It does not however, change the underlying hash table capacity. It does this by creating a new dynamic array with the original capacity. Sets self_size to 0.
        """
        self._buckets = DynamicArray()
        for elements in range(self._capacity):
            self._buckets.append(None)
        self._size = 0

    def get_keys_and_values(self) -> DynamicArray:
        """
        This method returns a dynamic array where each index contains a tuple of a key/value pair stored in the hash map. The order of the keys in the dynamic array may differ. Tombstone values are ignored.
        """
        new_arr = DynamicArray()
        for index in range(self._capacity):
            if self._buckets[index] is not None and not self._buckets[index].is_tombstone:
                new_arr.append((self._buckets[index].key, self._buckets[index].value))
        return new_arr

    def __iter__(self):
        """
        This method enables the hash map to iterate across itself. Initializes and returns a variable to track the iterator's progress through the hash map's contents.
        """
        self._index = 0
        return self

    def __next__(self):
        """
        This method returns the next item in the hash map based on the current location of the iterator.
        """
        while self._buckets[self._index] is None:
            self._index = (self._index + 1) % self._capacity
            if self._index == 0:
                raise StopIteration
        bucket = self._buckets[self._index]
        self._index = (self._index + 1) % self._capacity
        return bucket


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - my example")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(15):
        m.put('str' + str(i), i * 100)
        print(m)


    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - table_load example 1")
    print("--------------------------")
    m = HashMap(101, hash_function_1)
    print(round(m.table_load(), 2))
    m.put('key1', 10)
    print(round(m.table_load(), 2))
    m.put('key2', 20)
    print(round(m.table_load(), 2))
    m.put('key1', 30)
    print(round(m.table_load(), 2))

    print("\nPDF - table_load example 2")
    print("--------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(50):
        m.put('key' + str(i), i * 100)
        if i % 10 == 0:
            print(round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 1")
    print("-----------------------------")
    m = HashMap(101, hash_function_1)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 30)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key4', 40)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 2")
    print("-----------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('key' + str(i), i * 100)
        if i % 30 == 0:
            print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(23, hash_function_1)
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        if m.table_load() > 0.5:
            print(f"Check that the load factor is acceptable after the call to resize_table().\n"
                  f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))

    print("\nPDF - My example")
    print("----------------------")
    m = HashMap(10, hash_function_2)


    print("\nPDF - get example 1")
    print("-------------------")
    m = HashMap(31, hash_function_1)
    print(m.get('key'))
    m.put('key1', 10)
    print(m.get('key1'))

    print("\nPDF - get example 2")
    print("-------------------")
    m = HashMap(151, hash_function_2)
    for i in range(200, 300, 7):
        m.put(str(i), i * 10)
    print(m.get_size(), m.get_capacity())
    for i in range(200, 300, 21):
        print(i, m.get(str(i)), m.get(str(i)) == i * 10)
        print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)

    print("\nPDF - contains_key example 1")
    print("----------------------------")
    m = HashMap(11, hash_function_1)
    print(m.contains_key('key1'))
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key3', 30)
    print(m.contains_key('key1'))
    print(m.contains_key('key4'))
    print(m.contains_key('key2'))
    print(m.contains_key('key3'))
    m.remove('key3')
    print(m.contains_key('key3'))

    print("\nPDF - contains_key example 2")
    print("----------------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 20)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())
    result = True
    for key in keys:
        # all inserted keys must be present
        result &= m.contains_key(str(key))
        # NOT inserted keys must be absent
        result &= not m.contains_key(str(key + 1))
    print(result)

    print("\nPDF - remove example 1")
    print("----------------------")
    m = HashMap(53, hash_function_1)
    print(m.get('key1'))
    m.put('key1', 10)
    print(m.get('key1'))
    m.remove('key1')
    print(m.get('key1'))
    m.remove('key4')

    print("\nPDF - clear example 1")
    print("---------------------")
    m = HashMap(101, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key1', 30)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - clear example 2")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.get_size(), m.get_capacity())
    m.resize_table(100)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.resize_table(2)
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(12)
    print(m.get_keys_and_values())

    print("\nPDF - __iter__(), __next__() example 1")
    print("---------------------")
    m = HashMap(10, hash_function_1)
    for i in range(5):
        m.put(str(i), str(i * 10))
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)

    print("\nPDF - __iter__(), __next__() example 2")
    print("---------------------")
    m = HashMap(10, hash_function_2)
    for i in range(5):
        m.put(str(i), str(i * 24))
    m.remove('0')
    m.remove('4')
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)

