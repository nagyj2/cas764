def dataFromFile(fname):
	"""Function which reads from the file and yields a generator"""
	with open(fname, "r") as file_iter:
		for line in file_iter:
			line = line.strip().rstrip(",")  # Remove trailing comma
			record = line.split(",")
			yield record


def count_unique(fname):
	a = set(); c = 0
	for lst in dataFromFile(fname):
		for item in lst:
			if item not in a:
				a.add(item)
				c += 1
	return c


def count_dupes(fname):
	a = set(); b = set(); c = 0
	for lst in dataFromFile(fname):
		for thing in lst:
			if thing in a and thing not in b:
				c += 1
				b.add(thing)
			a.add(thing)
	return c


if __name__ == "__main__":

	files = ['Tesco.csv', 'Groceries.csv', 'Market_Basket_Optimisation.csv', 'INTEGRATED-DATASET.csv']

	for fname in files:
		print(f'Inside {fname}:')
		print(f'\tDistinct: {count_unique(fname)}')
		print(f'\tReoccur:  {count_dupes(fname)}')
