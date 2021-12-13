from BitHash import BitHash, ResetBitHash
from itertools import chain
import string
import random
import time

DEBUG = False

class Node(object):
    #constructor method create key and data attributes
    def __init__(self, key, data):
        self.key = key
        self.data = data
        
class CuckooHash(object):
    #constructor method create two hash arrays and a counter of keys
    def __init__(self, size):
        self.__hashArray1 = [None] * size
        self.__hashArray2 = [None] * size
        self.__numKeys = 0
        
    # return current number of keys in table    
    def __len__(self): return self.__numKeys    
        
    #hashes a string and returns two hash values as a tuple   
    def __hashFunc(self, s):
        v1 = BitHash(s) 
        v2 = BitHash(s, v1)
        return v1 % len(self.__hashArray1), v2 % len(self.__hashArray1)    
    
    #searches for a given key in the hash table, if found return its data,
    #if not return None
    def find(self, key):
        
        #hash the given key using two hash functions
        bucket1, bucket2 = self.__hashFunc(key)
        
        #check if node exists in either hash array and has the correct key
        #if found return the data
        if self.__hashArray1[bucket1] and self.__hashArray1[bucket1].key == key:
            return self.__hashArray1[bucket1].data
        
        elif self.__hashArray2[bucket2] and self.__hashArray2[bucket2].key == key:
            return self.__hashArray2[bucket2].data 
        
        #if no node found return none
        return None
    
    #deletes a given key from the hash table, return True upon success,
    #otherwise return false, key not inserted
    def delete(self, key): 
        
        #check to see if the key was inserted,
        #if key wasn't inserted then can't remove return False
        if self.find(key) == None:
            return False     
    
        #hash the given key using two hash functions
        bucket1, bucket2 = self.__hashFunc(key)        
        
        #check if  node exists in either hash array and has the correct key,
        #remove the node and decrement the key counter
        if self.__hashArray1[bucket1] and self.__hashArray1[bucket1].key == key:
            self.__hashArray1[bucket1] = None
            self.__numKeys -= 1
            
        elif self.__hashArray2[bucket2] and self.__hashArray2[bucket2].key == key:
            self.__hashArray2[bucket2] = None 
            self.__numKeys -= 1
            
        return True

    #increments a key's data by 1
    def incc(self, k):
        #hash the given key using two hash functions
        bucket1, bucket2 = self.__hashFunc(k)
        
        #check if  node exists in either hash array and has the correct key,
        #increment the data value in the node
        if self.__hashArray1[bucket1] and self.__hashArray1[bucket1].key == k:
            self.__hashArray1[bucket1].data += 1
        
        elif self.__hashArray2[bucket2] and self.__hashArray2[bucket2].key == k:
            self.__hashArray2[bucket2].data += 1

        #if the key does not exist, insert a 1
        else:
            self.insert(k, 1)

    #creates an iterator for the hash table
    def __iter__(self):
        def isEmpty(node):
            return node != None
        return chain(filter(isEmpty, self.__hashArray1),
                     filter(isEmpty, self.__hashArray2))

    #returns all key/ data pairs in the hashtable
    def items(self):
        for x in self:
            yield x.key, x.data

    #creates a node from a key, data pair and inserts a node into the hash table,
    #return True upon success, otherwise if node already in table, return False
    #account for hash table overflow and infinite looping
    def insert(self, key, data, count = 0):
        
        #check for infinite loops and reset bit hash
        #uses new hash functions to re-insert all the keys
        if count == 10:
            if DEBUG: print("count is", count)
            ResetBitHash()
            if DEBUG: print("resetting bit hash.")
            self.__copyHashTable()
            
        #if the hash arrays are full, grow the hash table
        if self.__numKeys >= len(self.__hashArray1)/2:
            self.__growHash()
            if DEBUG: print("Grew hash table.")
        
        #check to see if the key was already inserted,
        #if already inserted then can't insert again return False
        if self.find(key) != None:
            return False
        
        #hash the given key using two hash functions
        bucket1, bucket2 = self.__hashFunc(key)
        
        #try to insert into the first hash array, increment the key counter
        if not self.__hashArray1[bucket1]: 
            self.__hashArray1[bucket1] = Node(key, data)
            self.__numKeys += 1
            
        #if first is occupied insert into second hash array, increment the key counter   
        elif not self.__hashArray2[bucket2]: 
            self.__hashArray2[bucket2] = Node(key, data)  
            self.__numKeys += 1
        
        #if both buckets are occupied 
        #(use count to switch off which hash table gets a value 'popped'), 
        #kick out old node, insert new node in place of old node 
        elif count % 2 == 0:
            pop = self.__hashArray1[bucket1]
            self.__hashArray1[bucket1] = Node(key, data)
            
            #insert old node into second array
            #increment count to check for infinite loop
            self.insert(pop.key, pop.data, count+1)
        
        elif count % 2 == 1:
            pop2 = self.__hashArray2[bucket2]
            self.__hashArray2[bucket2] = Node(key, data)
            
            #insert old node into first array
            #increment count to check for infinite loop
            self.insert(pop2.key, pop2.data, count+1)
            
        return True
    
    #grows the hash table and rehashes all keys
    def __growHash(self):
        #calculate size of new hash table
        newSize = len(self.__hashArray1) * 2
        
        #rehash keys and insert into table
        self.__copyHashTable(newSize)
    
    #copies a hash table and accounts for size growth or no size growth,
    #rehashes all keys while inserting into correct place in hash table    
    def __copyHashTable(self, newSize = "newSize"):
        
        #if no arguement is given, 
        #initialize newSize to size of current hash table
        if newSize == "newSize":
            newSize = len(self.__hashArray1)
        
        #create a new hash table using new size
        newHashTable = CuckooHash(newSize)
        
        #loop through the old hash array and 
        #insert each value into the new hash table
        for i in range(len(self.__hashArray1)):
            node1 = self.__hashArray1[i]
            node2 = self.__hashArray2[i]
            
            #if node isn't None, insert into new hash table
            if node1:
                newHashTable.insert(node1.key, node1.data)
                
            if node2:
                newHashTable.insert(node2.key, node2.data)            
        
        #set the new hash arrays to the original reference        
        self.__hashArray1 = newHashTable.__hashArray1
        self.__hashArray2 = newHashTable.__hashArray2
        
        #set the new number of keys to the original reference  
        self.__numKeys = newHashTable.__numKeys   
 
###TEST CODE###        
def __test1():
    
    #inserts some values into hash table and checks find method        
    h = CuckooHash(100)          
    h.insert("A", "0")
    h.insert("B", "1")
    h.insert("C", "2")
    h.insert("D", "3")
    h.insert("E", "4")
    h.insert("F", "5")
    h.insert("G", "6")
    h.insert("H", "77")
    h.insert("IIII", "888")
    
    n = h.find("IIII")
    a = h.find("A")
    b = h.find("B")
    c = h.find("C")
    
    if n == "888":
        print("Success!")
    if a == "0":
            print("Success!")
    if b == "1":
            print("Success!")
    if c == "2":
            print("Your search method was successful!")      
    
def __test2():
    #calculates time per insert, from hash table class
    size = 91000
    
    t = time.time()
    h = CuckooHash(10)
    for i in range(size):
        h.insert(str(i+1000000000), i)
    t = time.time() - t
    print(t, "seconds  ", size/t, "inserts per second")
    return t, size/t
    
def __test3():
    #from hash table class
    size = 20000
    missing = 0
    
    # create a hash table with an initially small number of bukets
    h = CuckooHash(100)
    
    # Now insert size key/data pairs, where the key is a string consisting
    # of the concatenation of "foobarbaz" and i, and the data is i
    for i in range(size): 
        h.insert(str(i)+"foobarbaz", i)
        
    # Make sure that all key data pairs that we inserted can be found in the
    # hash table. This ensures that resizing the number of buckets didn't 
    # cause some key/data pairs to be lost.
    for i in range(size):
        ans = h.find(str(i)+"foobarbaz")
        if ans == None or ans != i:
            print(i, "Couldn't find key", i+"foobarbaz")
            missing += 1
            
    print("There were", missing, "records missing from CuckooHashTab")
    return missing

#really fun test code!    
def __test4():
    #initialize size to larger than size of hash table, checks grow function
    size = 1000
    
    #creates a bunch of random strings, 
    #saves to a list and checks if they were inserted
    start = time.time()
    c = CuckooHash(100)
    l = []
    for i in range(size):
        s = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for j in range(5))
        l += [s]
        print(s)
        print("It is", c.insert(s, i),"that the function inserted 1 item.")
        print("There are", len(c), "items in the hash table.")
    
    #choose an arbitrary number of keys to delete, deletes the given number of keys
    deletionNumber = 53
    
    for i in range(deletionNumber):
        print("It is", c.delete(l[i]),"that the item", l[i], "has been deleted.")
    
    #then re-inserts all keys from saved list, checking if only previous deleted keys succeed
    #counts how many keys were inserted
    count = 0
    for item in l:
        n = random.randint(1, 100)
        if c.insert(item, n) == True:
            count += 1        
            print("It is True that the function inserted 1 item.")
        else:
            print("It is", c.insert(s, i),"that the function inserted 1 item.")
    end = time.time()
    
    #checks if count matches number deleted
    if count == deletionNumber:
        print("Success! The duplicate keys weren't inserted.")
        
    else:
        print("Faliure! Check your deletion method. Check your insertion method.")
    return end-start, count
               
def __main():
    __test1()

    record = [[0,0],[0,],[0,0]]
    N = 20

    for i in range(N):
        t_insert_time, t_inserts_per_second = __test2()
        t_grow = __test3()
        t_delete_time, t_delete_amount = __test4()
        
        record[0][0] += t_insert_time
        record[0][1] += t_inserts_per_second
        record[1][0] += t_grow
        record[2][0] += t_delete_time
        record[2][1] += t_delete_amount

    print(f"Average time to insert {N} times: {record[0][0]/N} seconds")
    print(f"Average inserts per second: {record[0][1]/N}")
    print(f"Average missing values on growth: {record[1][0]/N}")
    print(f"Average time to delete {N} times: {record[2][0]/N} seconds")
    print(f"Average deletes per second: {record[2][1]/N}")

if __name__ == '__main__':
    __main()

# 3.954s, 23025.745 insert/s
# 0 missing
# 0.0480s, 53 insert
