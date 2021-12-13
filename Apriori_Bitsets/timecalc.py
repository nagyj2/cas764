import time, bitarray, bitarray.util

TEST_STR = '11001'
MAXS = len(TEST_STR)

def bit_subsets(bits):
	'''Compute all bitsets of same length which are subsets of bits'''
	global MAXS
	def isSubset(obits):
		while len(obits) < len(bits):
			obits.insert(0,0)
		# print(obits,obits & bits)
		return bitarray.util.count_and(obits, bits) and (obits | bits).count() <= bits.count()
	return filter(isSubset, map(bitarray.bitarray, [f'{x:b}' for x in range(2 ** (MAXS))]))

def actual_bit_subsets(bits):
		'''Compute all bitsets of same length which are subsets of bits'''
		global MAXS
		def isSubset(obits):
				# print(obits,obits & bits)
				print(obits, bitarray.util.count_and(obits, bits), (obits | bits).count() <= bits.count())
				return bitarray.util.count_and(obits, bits) and (obits | bits).count() <= bits.count()
		return filter(isSubset, map(bitarray.bitarray, [f'{x:b}'.zfill(MAXS) for x in range(2 ** (MAXS))]))


def new_bit_subsets(bits):
	'''Compute all bitsets of same length which are subsets of bits'''
	global MAXS
	def isSubset(obits):
		# print(obits,obits & bits)
		return bitarray.util.count_and(obits, bits) and (obits | bits).count() <= bits.count()
	return filter(isSubset, map(bitarray.bitarray, [f'{x:b}'.zfill(MAXS) for x in range(2 ** (MAXS))]))

def recursive_bit_subsets(bits, index=0, ret = set()):
	global MAXS
	if index == len(bits) - 1:
		return ret
	index += 1

	# s = s[:position] + replacement + s[position+length_of_replaced:]
	# print(bits, index)

	less = bitarray.frozenbitarray(bits.to01()[:index] + '0' + bits.to01()[index+1:])
	if bits[index] == 1:
		# print (bits,less)
		if less.any():
			ret.add(less)
		ret.add(bits)
		# MSB is 1, so keep and recurse
		recursive_bit_subsets(bits, index, ret)

	recursive_bit_subsets(less, index, ret)
	return ret

start = time.time()
sets = bit_subsets(bitarray.frozenbitarray(TEST_STR))
old = time.time() - start

print(f'old: {old}s')

start = time.time()
actual_sets = actual_bit_subsets(bitarray.frozenbitarray(TEST_STR))
actual = time.time() - start

print(f'actual: {actual}s')

start = time.time()
new_sets = new_bit_subsets(bitarray.frozenbitarray(TEST_STR))
new = time.time() - start
print(f'new: {new}s')

start = time.time()
recursive_sets = recursive_bit_subsets(bitarray.frozenbitarray(TEST_STR))
recursive = time.time() - start
print(f'recursive: {recursive}s')


lst = list(sets)
new_lst = list(new_sets)
actual_lst = list(actual_sets)
recursive_lst = list(recursive_sets)

lst.sort()
new_lst.sort()
actual_lst.sort()
recursive_lst.sort()

print(f'''---------- RESULTS
size: {MAXS}
len old: {len(lst)}
len actual: {len(actual_lst)}
len new: {len(new_lst)}
len recursive: {len(recursive_sets)}'''
)

for x in lst: print(x, end=' ')
print('')
for x in new_lst: print(x, end=' ')
print('')
for x in actual_lst: print(x, end=' ')
print('')
for x in recursive_lst: print(x, end=' ')
print('')

# print(f'''list old: {lst}
# list new: {new_lst}
# list recursive {recursive_list}''')


# TESTS = 100000

# start = time.time()
# for _ in range(TESTS):
# 	s = '0' * (MAXS - len(f'{1 << MAXS:b}')) + f'{1 << MAXS:b}'
# end = time.time()
# print(f'text: {end-start}')

# start = time.time()
# for _ in range(TESTS):
# 	s = f'{1 << MAXS:b}'.zfill(MAXS)
# end = time.time()
# print(f'zfill: {end-start}')
