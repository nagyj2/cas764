"""
Description     : Simple Python implementation of the Apriori Algorithm

Usage:
    $python apriori.py -f DATASET.csv -s minSupport  -c minConfidence

    $python apriori.py -f DATASET.csv -s 0.15 -c 0.6

    $python apriori.py -f Groceries.csv -s 0.05 -c 0.2

Modified to use bitarrays instead of sets and frozen sets
"""

import sys, time, bitarray, bitarray.util

from itertools import chain, combinations
from collections import defaultdict
from optparse import OptionParser

#. Maximum number of bits in a bitset
MAXS = 200
convDict = {}

# def subsets(arr):
#     """ Returns non empty subsets of arr"""
#     return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])

#. Save results into a dict and then if a new attempt is a subset of a previous attempt, go based off it
def bit_subsets(bits):
    '''Compute all bitsets of same length which are subsets of bits'''
    global MAXS
    return filter(
        lambda obits: bitarray.util.count_and(obits, bits) and (obits | bits).count() <= bits.count(), 
        map(bitarray.bitarray, [
            f'{x:b}'.zfill(MAXS) for x in range(2 ** MAXS)
        ])
    )


def pprint(bitarr):
    global MAXS, convDict
    invdct = {v: k for k, v in convDict.items()}
    string = '{'
    for pos, item in enumerate(bitarr):
        if item:
            string += invdct[MAXS - 1 - pos] + ','
    string += '}'
    return string



def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
    """calculates the support for items in the itemSet and returns a subset
    of the itemSet each of whose elements satisfies the minimum support"""
    _itemSet = set()
    localSet = defaultdict(int)

    for item in itemSet: 
        #. item is a frozenbitarray
        for transaction in transactionList:
            #. transaction is frozenbitarray
            if bitarray.util.count_and(item, transaction) >= item.count():
                freqSet[item] += 1
                localSet[item] += 1

    for item, count in localSet.items():
        support = float(count) / len(transactionList)

        if support >= minSupport:
            _itemSet.add(item)

    return _itemSet


def joinSet(itemSet, length): #. itemSet is now contains bitarrays
    """Join a set with itself and returns the n-element itemsets"""
    return set(
        # [i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length]
        [i | j for i in itemSet for j in itemSet if bitarray.util.count_or(i,j) == length]
    )


def getItemSetTransactionList(data_iterator):
    global MAXS
    transactionList = list()
    itemSet = set()
    track, n = dict(), 0
    for record in data_iterator:
        transaction = 0 # base number
        for item in record:
            #? Faster to simply add and then check item in track later
            if not item in track:
                track[item] = n
                elemSet = bitarray.frozenbitarray(f'{1 << n:b}'.zfill(MAXS))    # Generate 1-itemSets
                itemSet.add(elemSet)                            # Add i-itemSets
                
                n += 1  # Increment counter
                if (n > MAXS):
                    print("maximum number of elements reached")
                    quit()

            transaction |= 1 << track[item] # Shift 1 over x times and or it to the transaction
            # itemSet.add(frozenset([item]))

        transactionList.append( bitarray.frozenbitarray(f'{transaction:b}'.zfill(MAXS)) )

    print(f"alloc = {n}")
    # MAXS = n # Update MAXS to avoid wasting bits

    #$ Debug Printing
    # print(track)
    # for item in itemSet: print(f"Item: {item}")
    # for trans in transactionList: print(f"Trans: {trans}")

    return itemSet, transactionList, track


def runApriori(data_iter, minSupport, minConfidence):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
    """
    global MAXS, convDict

    start = time.time()
    itemSet, transactionList, convDict = getItemSetTransactionList(data_iter)
    #. itemSet : Set of frozenbitarray repr. the significant item sets (value=large itemset)
    #. transactionList : Array of frozenbitarray repr. all transaction's contents (value=each transaction)
    #. convDict : Mapping from element text to frozenbitarray bit index (key=dataset string,value=bit number)

    freqSet = defaultdict(int) #. Index by itemSet element. Stores count of elements
    largeSet = dict() #. Stores historical bit arrays by k-itemsets that satisfy minSupport (key=n-itemSets,value=support)

    assocRules = dict()
    # Dictionary which stores Association Rules

    oneCSet = returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet)

    currentLSet = oneCSet
    k = 2
    while currentLSet != set([]):
        largeSet[k - 1] = currentLSet
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(
            currentLSet, transactionList, minSupport, freqSet
        )
        currentLSet = currentCSet
        k = k + 1

    end = time.time()
    print(f'Sep.: {end-start}s')

    def getSupport(item):
        """local function which Returns the support of an item"""
        return float(freqSet[item]) / len(transactionList)

    toRetItems = []
    for key, value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item)) for item in value])

    toRetRules = set()
    #. All possible subsets as a list. NOTE: Not all the proper size
    for key, value in list(largeSet.items())[1:]:
        for item in value:
            _subsets = bit_subsets(item) # return filter of bitsets that are subsets of item
            for element in _subsets:
                remain = item & ~element # subtract bitsets
                if remain.any():
                    confidence = getSupport(item) / getSupport(element)
                    if confidence >= minConfidence:
                        toRetRules.add(((tuple(element), tuple(remain)), confidence))


    end = time.time()
    print(f'Coll.: {end-start}s')
    return toRetItems, toRetRules


def printResults(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    print(f"\n---------- ITEMS ({len(items)}):")
    for item, support in sorted(items, key=lambda x: x[1]):
        print(f"Item: {pprint(item)} , {support:.3f}")
    print(f"\n---------- RULES ({len(rules)}):")
    for rule, confidence in sorted(rules, key=lambda x: x[1]):
        pre, post = rule
        print(f"Rule: {pprint(pre)} ==> {pprint(post)} , {confidence:.3f}")


def to_str_results(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    i, r = [], []
    for item, support in sorted(items, key=lambda x: x[1]):
        x = "item: %s , %.3f" % (str(item), support)
        i.append(x)

    for rule, confidence in sorted(rules, key=lambda x: x[1]):
        pre, post = rule
        x = "Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence)
        r.append(x)

    return i, r

#todo merge functionality from getItemSetTransactionList to here
def dataFromFile(fname):
    """Function which reads from the file and yields a generator"""
    with open(fname, "r") as file_iter:
        for line in file_iter:
            line = line.strip().rstrip(",")  # Remove trailing comma
            record = frozenset(line.split(","))
            yield record

if __name__ == "__main__":

    import cProfile, pstats, tracemalloc, os, linecache
    def display_top(snapshot, key_type='lineno', limit=3):
        snapshot = snapshot.filter_traces((
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        ))
        top_stats = snapshot.statistics(key_type)

        print("Top %s lines" % limit)
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            # replace "/path/to/module/file.py" with "module/file.py"
            filename = os.sep.join(frame.filename.split(os.sep)[-2:])
            print("#%s: %s:%s: %.1f KiB"
                % (index, filename, frame.lineno, stat.size / 1024))
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                print('    %s' % line)

        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))
        
    profiler = cProfile.Profile()

    optparser = OptionParser()
    optparser.add_option(
        "-f", 
        "--inputFile", 
        dest="input", 
        help="filename containing csv", 
        default=None
    )
    optparser.add_option(
        "-s",
        "--minSupport",
        dest="minS",
        help="minimum support value",
        default=0.15,
        type="float",
    )
    optparser.add_option(
        "-c",
        "--minConfidence",
        dest="minC",
        help="minimum confidence value",
        default=0.6,
        type="float",
    )

    (options, args) = optparser.parse_args()

    inFile = None
    if options.input is None:
        inFile = sys.stdin
    elif options.input is not None:
        inFile = dataFromFile(options.input)
    else:
        print("No dataset filename specified, system with exit\n")
        sys.exit("System will exit")

    minSupport = options.minS
    minConfidence = options.minC

    tracemalloc.start()
    profiler.enable()
    items, rules = runApriori(inFile, minSupport, minConfidence)
    profiler.disable()
    snapshot = tracemalloc.take_snapshot()

    stats = pstats.Stats(profiler)
    stats.sort_stats('ncalls')
    stats.print_stats()
    display_top(snapshot)

    printResults(items, rules)
