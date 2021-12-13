import bitarray, bitarray.util

def subsets(nums):
	temp_result = []
	subsets_util(nums,[0 for i in range(len(nums))],temp_result,0)
	main_result = []
	for lists in temp_result:
			temp = []
			for i in range(len(lists)):
				if lists[i] == 1:
						temp.append(nums[i])
			main_result.append(temp)
	return main_result

def subsets_util(nums,temp,result,index):
	if index == len(nums):
			result.append([i for i in temp])
			#print(temp)
			return
	temp[index] = 0
	subsets_util(nums,temp,result,index+1)
	temp[index] = 1
	subsets_util(nums, temp, result,index + 1)

def b_subsets(bits):
	temp_result = []
	b_all_subsets(bits,[0 for i in range(len(bits))],temp_result,0)
	main_result = []
	# print(temp_result)
	for lists in temp_result:
			temp = []
			for i in range(len(lists)):
				print(lists,lists[i])
				if lists[i] == 1:
						temp.append(bitarray.frozenbitarray('0' * (len(bits) - len(bin(i)[2:]))) + bin(lists[i])[2:] )
			main_result.append(temp)
	# return main_result

def b_all_subsets(bits,temp,result,index):
	if index == len(bits):
			result.append([i for i in temp])
			#print(temp)
			return
	temp[index] = 0
	b_all_subsets(bits,temp,result,index+1)
	temp[index] = 1
	b_all_subsets(bits, temp, result,index + 1)

# print(subsets([1,2,3,4]))
# print(b_subsets(bitarray.frozenbitarray('001100101')))

from itertools import chain, combinations
def subsets(arr):
    """ Returns non empty subsets of arr"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])

def subset(bits, MAXS=6):
	'''Compute all bitsets of same length which are subsets of bits'''

	def isSubset(obits):
		while len(obits) < len(bits):
			obits.insert(0,0)
		
		print(obits,obits & bits)

		return bitarray.util.count_and(obits, bits) and (obits | bits).count() <= bits.count()

	return list(filter(isSubset, map(bitarray.bitarray, [f'{x:b}' for x in range(2 ** (MAXS-1))])))

print(subset(bitarray.frozenbitarray('01101')))
