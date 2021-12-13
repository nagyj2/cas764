from BitHash import BitHash, ResetBitHash
from itertools import chain
import string, random, time, csv

DEBUG = False

class Node(object):
	#constructor method create key and data attributes
	def __init__(self, key, data):
		self.key = key
		self.data = data
		
class CuckooHash(object):
	#constructor method create two hash arrays and a counter of keys
	def __init__(self, size, maxstash = 5, maxloop = 100):
		self.__hashArray1 = [None] * int(size)
		self.__hashArray2 = [None] * int(size)
		self.__numKeys = 0

		self.__stack = []
		self.__MAXSTASH = maxstash
		# self.__leftover = None
		self.__capacity = len(self.__hashArray1) + len(self.__hashArray2) + self.__MAXSTASH

		self.__MAXLOOP = maxloop
		self.duetoloop = None # tracker to see why there was a rehash

		self.lf = 0.8
		
	# return current number of keys in table    
	def __len__(self): return self.__numKeys
	
	# return maximum capacity of the table
	def capacity(self): return self.__capacity
		
	#hashes a string and returns two hash values as a tuple   
	def __hashFunc(self, s):
		v1 = BitHash(s) 
		v2 = BitHash(s, v1)
		return v1 % len(self.__hashArray1), v2 % len(self.__hashArray1)    
	
	def debug_stash(self, key, data):
		self.__stash(key,data)

	def debug_stash_show(self):
		for node in self.__stack:
			print(node.key,node.data)

	def debug_stash_size(self):
		return len(self.__stack)

	#stash data in the internal stash array
	def __stash(self, key, data, i=0):
		'''Returns True if the table was enlargened. False otherwise'''
		node = Node(key, data)
		self.__numKeys += 1 # increase b/c either we stash or rehash + insert

		if DEBUG: print(f'Stashing {key}')
		if len(self.__stack) < self.__MAXSTASH:
			if DEBUG: print("stashed")
			self.__stack.append(node)
			return False

		# self.__leftover = node

		# If the stash is full (self.__MAXSTASH items), reset the functions and reset the table
		ResetBitHash()
		if DEBUG: print(f'REHASH: Loop ({i})')
		self.__growHash() # removes stash, leftover and rehashes everything
		self.insert(key, data) # inserts the leftover
		self.duetoloop = True
		return True

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

		for node in self.__stack:
			if node.key == key:
				return node.data
		
		#if no node found return none
		return None
	
		#creates a node from a key, data pair and inserts a node into the hash table,
	
	#return True upon success, otherwise if node already in table, return False
	#account for hash table overflow and infinite looping
	def insert(self, key, data, count = 0):

		# if count == 0:
		# 	print(self.__numKeys / self.__capacity) 

		# If insertion has gone long enough,
		if count >= self.__MAXLOOP:
			# Stash the item into the structure
			self.__stash(key, data, i=count)
			
			# Items were stashed or stash and leftover were reinserted into the table on rehash
			return True

		
		#If load factor is greater than 0.5, rehash the table
		if count == 0 and (self.__numKeys / self.__capacity) > self.lf:
			# full = self.__stash(key, data)
			if DEBUG: print("REHASH: Load Factor")

			# if full:
			self.__growHash() # removes stash and rehashes everything
			self.duetoloop = False
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
	
	#deletes a given key from the hash table, return True upon success,
	#otherwise return false, key not inserted
	def delete(self, key): 
		'''Delete the stored element at `key` and return true if successful. Return false otherwise.'''
		#check to see if the key was inserted,
		#if key wasn't inserted then can't remove return False
		if self.find(key) == None:
			return False     

		#we know the key is in the table
		self.__numKeys -= 1
	
		#hash the given key using two hash functions
		bucket1, bucket2 = self.__hashFunc(key)        
		
		#check if  node exists in either hash array and has the correct key,
		#remove the node and decrement the key counter
		if self.__hashArray1[bucket1] and self.__hashArray1[bucket1].key == key:
			self.__hashArray1[bucket1] = None
			
		elif self.__hashArray2[bucket2] and self.__hashArray2[bucket2].key == key:
			self.__hashArray2[bucket2] = None 
		
		for node in self.__stack:
			if node.key == key: 
				self.__stack.remove(node)
				break
			
		return True
 

	def incc(self, key):
		'''Find a key `key` and increment its data value by 1. If no `key` is found, insert 1 at `key`.'''
		#hash the given key using two hash functions
		bucket1, bucket2 = self.__hashFunc(key)
		
		#check if  node exists in either hash array and has the correct key,
		#increment the data value in the node
		if self.__hashArray1[bucket1] and self.__hashArray1[bucket1].key == key:
			self.__hashArray1[bucket1].data += 1
		
		elif self.__hashArray2[bucket2] and self.__hashArray2[bucket2].key == key:
			self.__hashArray2[bucket2].data += 1

		#if the key does not exist, insert a 1
		else:
			for node in self.__stack:
				if node.key == key:
					node.data += 1
					return

			self.insert(key, 1)


	#creates an iterator for the hash table
	def __iter__(self):
		def isEmpty(node):
			return node != None
		return chain(filter(isEmpty, self.__hashArray1),
					 filter(isEmpty, self.__hashArray2),
					 self.__stash) # self.__leftover should never have anything in it

	#returns all key/ data pairs in the hashtable
	def items(self):
		for x in self:
			yield x.key, x.data

	#grows the hash table and rehashes all keys
	def __growHash(self):
		#calculate size of new hash table
		newSize = len(self.__hashArray1) * 2
		
		#rehash keys and insert into table
		self.__copyHashTable(newSize)
	
	#copies a hash table and accounts for size growth or no size growth,
	#rehashes all keys while inserting into correct place in hash table    
	#flushes the stash and leftover
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

		for nodeS in self.__stack:
			newHashTable.insert(nodeS.key, nodeS.data)
		
		# if self.__leftover:
		# 	newHashTable.insert(self.__leftover.key, self.__leftover.data)
		
		#set the new hash arrays to the original reference        
		self.__hashArray1 = newHashTable.__hashArray1
		self.__hashArray2 = newHashTable.__hashArray2
		self.__stack = newHashTable.__stack
		# self.__leftover = newHashTable.__leftover #! should always be None
		
		#set the metadata  
		self.__numKeys = newHashTable.__numKeys
		self.__capacity = newHashTable.__capacity
		self.duetoloop = None # Taken care of by caller to __copyHashTable
 
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
	
def __test2(size=91000):
	#calculates time per insert, from hash table class
	# size = 91000
	
	t = time.time()
	h = CuckooHash(10)
	for i in range(size):
		h.insert(str(i+1000000000), i)
	t = time.time() - t
	print(t, "seconds  ", size/t, "inserts per second")
	return t, size/t
	
def __test3(size = 20000):
	#from hash table class
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
def __test4(size = 1000):
	#initialize size to larger than size of hash table, checks grow function
	
	#creates a bunch of random strings, 
	#saves to a list and checks if they were inserted
	start = time.time()
	c = CuckooHash(size // 10)
	l = []
	for i in range(size):
		s = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for j in range(5))
		l += [s]
		print(s)
		print("It is", c.insert(s, i),"that the function inserted 1 item.")
		print("There are", len(c), "items in the hash table.")
	
	#choose an arbitrary number of keys to delete, deletes the given number of keys
	deletionNumber = size // 20
	
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
		t_insert_time, t_inserts_per_second = __test2(125000)
		t_grow = __test3(50000)
		t_delete_time, t_delete_amount = __test4(2000)
		
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

# 
# 4.0247s, 22611.8 insert/s
# 0 missing
# 0.0488s, 53 insert
