import time, random, string, csv
from functools import reduce

from stashhash import CuckooHash as StackHash

###TEST CODE###        
def __test_basic_op(stashsize, maxloop):
		
		#inserts some values into hash table and checks find method        
		h = StackHash(100, stashsize, maxloop)          
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
		print('Completed basic test')   
		
def __test_excessive_inserts(stashsize, maxloop, size=91000):
	'''Insert a large amount of elements into a hashtable and check speed'''
	#calculates time per insert, from hash table class
	# size = 91000
	
	t = time.time()
	h = StackHash(10, stashsize, maxloop)
	for i in range(size):
			h.insert(str(i+1000000000), i)
	t = time.time() - t
	print(t, "seconds  ", size/t, "inserts per second")
	return t
		
def __test_excessive_find(stashsize, maxloop, size = 20000):
	'''Add a number of elements to a hashtable and then ensure every one is within the table'''
	#from hash table class
	missing = 0
	
	
	# create a hash table with an initially small number of bukets
	h = StackHash(100, stashsize, maxloop)
	
	# Now insert size key/data pairs, where the key is a string consisting
	# of the concatenation of "foobarbaz" and i, and the data is i
	for i in range(size): 
			h.insert(str(i)+"foobarbaz", i)
			
	start = time.time()
	# Make sure that all key data pairs that we inserted can be found in the
	# hash table. This ensures that resizing the number of buckets didn't 
	# cause some key/data pairs to be lost.
	for i in range(size):
			ans = h.find(str(i)+"foobarbaz")
			if ans == None or ans != i:
					print(i, "Couldn't find key", i+"foobarbaz")
					missing += 1
	end = time.time()
					
	print("There were", missing, "records missing from CuckooHashTab")
	return end - start, missing

#really fun test code!    
def __test_reinsert(stashsize, maxloop, size = 1000):
	'''Populate a table, remove elements and then try to reinsert. returns number of correct reinserts and skips'''
	#initialize size to larger than size of hash table, checks grow function
	
	#creates a bunch of random strings, 
	#saves to a list and checks if they were inserted
	start = time.time()
	h = StackHash(size // 10, stashsize, maxloop)
	l = []
	for i in range(size):
		s = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for j in range(5))
		l += [s]
		h.insert(s, i)
	
	old_size = len(h)
	print(f"There are {old_size} items in the hash table.")
	
	#choose an arbitrary number of keys to delete, deletes the given number of keys
	deleteNominal, deleteActual = size // 20, 0 # Number to delete, number actually deleted (if there is a duplicate choice, forget it)
	c = []
	
	for _ in range(deleteNominal):
		w = random.choice(l)
		if h.delete(w):
			c += [w]
			deleteActual += 1

	delete_size = len(h)
	if (delete_size == old_size - deleteActual):
		print(f"There are now {delete_size} items in the hash table after deleting {deleteActual} elements.")
	else:
		print(f"FAILURE!! There are now {delete_size} items in the hash table after deleting {deleteActual} elements.")

	
	#then re-inserts all keys from saved list, checking if only previous deleted keys succeed
	#counts how many keys were inserted
	reinserts, skips = 0, 0
	for item in l:
		if h.insert(item, -1): # reinsertion worked!
			reinserts += 1
			c.remove(item)
			# print(f"Reinserted {item}")
		else:
			skips += 1 # Already in table, so skip
			# print(f"Skipped {item}")

	new_size = len(h)
	print(f"There are now {new_size} items in the hash table after reinserting {reinserts} elements.")
	end = time.time()
	
	#checks if count matches number deleted
	if new_size == old_size:
		print("The duplicate keys weren't inserted.")
			
	else:
		print("FAILURE!! Check your deletion method. Check your insertion method.")
		print(f'missing {c} keys')
	return end - start, new_size - old_size

def __test_loop_detection(stashsize, maxloop, size = 1000):
	'''Find how many loops are detected for given input size and the rate/ timing of rehashes'''
	
	# create a hash table with an initially small number of slots
	h = StackHash(100, stashsize, maxloop)
	
	# tracker for rehash count and the current size
	rehash, dueto, f_cap = 0, [], 100

	# insert elements into the hash table, looking for rehashes
	for i in range(size): 
			h.insert(str(i)+"foobarbaz", i)

			if h.duetoloop != None:
				rehash += 1
				f_cap = h.capacity()
				dueto.append(True if h.duetoloop else False)
				h.duetoloop = None

	print(f'There were {rehash} rehashes for {size} inserts. Ending capacity was {f_cap}')
	num = reduce(lambda old, duetoloop : old*10 + (1 if duetoloop else 2), dueto, 0)
	print(f'1: Loop, 2: LF >> S {num} E')
	return rehash, f_cap, num

def find_num_to_rehash(stash, loop, init):
	'''Find the number of elements to insert to cause a rehash'''
	h = StackHash(init, stash, loop)

	# insert elements into the hash table, looking for rehashes
	for i in range(init * 2): 
			# print(f'{len(h)}/{h.capacity()} elements >>')
			h.insert(str(i)+"foobarbaz", i)

			if h.duetoloop != None:
				print(f'{i} : {"Insertion Loop" if h.duetoloop else "Load Factor"}')
				return i, h.duetoloop
				if h.duetoloop:
					# print(f'{i} : Insertion Loop')
					return i, True
				else:
					# print(f'{i} : Load Factor')				
					return i, False

	print("Need more elements")
	return -1, None

def __main():
		
		# Base numbers to define the test
		base_inserts  =  250000
		base_finds    =  250000
		base_complex  =   10000
		base_initsize =     100
		# Factors of base numbers to actually test
		factors = [0.5, 0.75, 1, 1.25, 1.50, 2]
		# Create actual test cases
		inserts  = list(map(lambda x: int(base_inserts  * x), factors))
		finds    = list(map(lambda x: int(base_finds    * x), factors))
		complex  = list(map(lambda x: int(base_complex  * x), factors))
		initsize = list(map(lambda x: int(base_initsize * x), factors))
		# Times to perform each test
		times = 10

		fname = f'./tests/StackHash(ReHash)_test_{base_inserts}_{base_finds}_{base_complex}.csv'
		with open(fname, 'a', newline='') as csvfile:
			writer = csv.writer(csvfile)
			if csvfile.tell() == 0:
				writer.writerow(['stash_size', 'max_loop', 'init_size', 'inserts', 'elem_to_rehash', 'rehash_due_to_loop', 'num_of_rehashes', 'final_capacity', 'rehash_history'])
				writer.writerow(['',           ''        , ''         , ''       , ''              , ''                  , ''               , ''              , ''              ])
		
			for maxloop in [10, 25, 50, 100]:
				for stashsize in [0, 3, 5, 10, 15]:
					__test_basic_op(stashsize, maxloop)
					for i in range(len(inserts)):

						for time in range(times):

							# Keep inserting elements until the table rehashes
							t_elem_rehash, t_rehash_bc_loop = find_num_to_rehash(stashsize, maxloop, initsize[i])

							# Insert some amount of elements, tracking the number of rehashes, history of rehashes and final table capacity
							t_rehashes, t_final_capacity, t_rehash_hist = __test_loop_detection(stashsize, maxloop, inserts[i])
							
							writer.writerow([stashsize, maxloop, initsize[i], inserts[i], t_elem_rehash, t_rehash_bc_loop, t_rehashes, t_final_capacity, t_rehash_hist])
							print(f'StashHash(ReHash,{stashsize},{maxloop}) loop for: {inserts[i]}, {initsize[i]} x {time+1} done')


		# for maxloop in [10, 25, 50, 100]:
		# 	for stashsize in [0, 3, 5, 10, 15]:
		# 		__test_basic_op(stashsize, maxloop)

		# 		fname = f'./tests/StackHash(ReHash,{stashsize},{maxloop})_test_{base_inserts}_{base_finds}_{base_complex}.csv'
		# 		with open(fname, 'a', newline='') as csvfile:
		# 			writer = csv.writer(csvfile)
		# 			if csvfile.tell() == 0:
		# 				writer.writerow(['stash_size', 'max_loop', 'init_size', 'elem_to_rehash', 'rehash_due_to_loop'])
		# 				writer.writerow(['',           ''        , ''         , ''              , ''                  ])

		# 			for i in range(len(inserts)):
		# 				for time in range(times):

		# 					t_elem_rehash, t_rehash_bc_loop = find_num_to_rehash(stashsize, maxloop, initsize[i])

		# 					# Perform exhaustive insert test
		# 					t_rehashes, t_final_capacity, t_rehash_hist = __test_loop_detection(stashsize, maxloop, inserts[i])
							
		# 					writer.writerow([stashsize, maxloop, complex[i], t_rehashes, initsize[i]])
		# 					print(f'StashHash(ReHash,{stashsize},{maxloop}) loop for: {inserts[i]}, {finds[i]}, {complex[i]} x {time+1} done')


if __name__ == '__main__':
	__main()
	# find_num_to_rehash(stash = 0, loop = 100, init = 100)
	# find_num_to_rehash(stash = 5, loop = 100, init = 100)

	# __test_loop_detection(20, 100, size = 100000)
