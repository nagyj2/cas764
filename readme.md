## Optimizing Data Structures for the Apriori Algorithm

This repositiory is all the code used for creating my final project for the course **CAS 764** at McMaster University.
Please excuse the mess. I admit I did not do a good job at organizing this repo. It was mainly used as a collection of files.

Below is a quick rundown of the important directories and files:

- `Apriori_Base/`: The basic apriori implementation used. It was taken from Github user asaini's [Apriori Github repo](https://github.com/asaini/Apriori).
- `Apriori_Bitsets/`: A bitset adapted version of `Apriori_Base/`.
- `Apriori_Cuckoo/`: Where Cuckoo hash table tests were performed.
	- `cuckoohash.py`: Base Cuckoo hash table implementation. Taken from a repo, but modified for correctness.
	- `stashhash.py`: My optimized Cuckoo hash table implementation. Based off `cuckoohash.py`.
	- `hash_test.py`: The file containing test cases and csv writing capability.
	- `tests/`: Where all tests csv files are kept.
		- `StashSize/`: Test data on varying stash sizes.
		- `LoopSize/`: Test data on varying loop iteration limit.
		- `LoopDetect/`: Test data on an attempt to better implement loop detection.
- `bitarray`: The library used to implement bit sets.
