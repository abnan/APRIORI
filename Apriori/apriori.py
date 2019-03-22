"""
Student Name: Abhishek Nan

Sample usage: python3 apriory.py dataT10K500D12L.data.txt 0.01 0.8

Commandline arguments:
    1: file name
    2: minimum support
    3: minimum confidence
    4: r|f|a|
        r - all strong association rules are output
        f - all frequent itemsets are output
        a - all frequent itemsets and all strong association rules are output
         - (leaving it blank) the number of frequent itemsets of different sizes and the number of strong rules are output

Output: The output is produced in a file in the same directory named apriori_output.txt
"""


import itertools
import time
import math
import sys
import getopt

def main(argv):
    t0 = time.clock()
    filename = argv[0]
    support = float(argv[1])
    confidenceThreshold = float(argv[2])
    if(len(argv)>3):
        displayOption = argv[3]
    else:
        displayOption = "absent"
    if(support<0 or support>1 or confidenceThreshold<0 or confidenceThreshold>1):
        print("Support and Confidence must be numbers between 0 and 1.")
        exit()
    #set numberofTransactions to 0 if you just want to read the entire file, set it to n if you want to read n lines
    numberofTransactions=0
    allTransactions = getAllTransactions(filename)
    totalNumOfTransactions = len(allTransactions)
    if(numberofTransactions>0):
        numberofTransactions = totalNumOfTransactions if numberofTransactions > totalNumOfTransactions else numberofTransactions
    else:
        numberofTransactions = totalNumOfTransactions
    supportValue = support*numberofTransactions
    # supportValue = support
    allTransactions = allTransactions[0: numberofTransactions]
    splitAllTransactions = [transaction.split() for transaction in allTransactions]
    countDictionary = {}
    max_transaction_len=0
    for transaction in splitAllTransactions:
        temp_len = len(transaction)
        if(temp_len>max_transaction_len):
            max_transaction_len = temp_len
        for item in transaction:
            if(frozenset([item]) in countDictionary):
                countDictionary[frozenset([item])]+=1
            else:
                countDictionary[frozenset([item])]=1
    transactionSets=[]
    for transaction in splitAllTransactions:
        transactionSets.append(frozenset(transaction))
    finalCandidateswSupport = {}
    prunedList = calcSupportAndPrune(countDictionary, supportValue)
    f = open("apriori_output.txt", "w")
    if(displayOption=="absent"):
        print("Number of frequent 1_itemsets:", len(prunedList), file = f)
    finalCandidateswSupport.update(prunedList)

    #start loop from 2 since length 1 case is handled above
    for loopctr in range(2, max_transaction_len+1):
        #Generate next set of candidates
        newCandidates = generateNextCandidateSet(prunedList)     
        #Count occurences of these candidates           
        getItemSetCounts(newCandidates, transactionSets, loopctr) 
        #Prune them according to minimum support
        prunedList = calcSupportAndPrune(newCandidates, supportValue)
        if(displayOption=="absent"):
            if(len(prunedList)==0):
                break
            else:
                print("Number of frequent %d_itemsets: %d" % (loopctr, len(prunedList)), file = f)
        finalCandidateswSupport.update(prunedList)

    confidenceDict={}
    for finalCandidate in finalCandidateswSupport:
        lenOfCandidate=len(finalCandidate)
        if(lenOfCandidate>1):
            #For subsets of each differnt possible length
            for subsetLen in range(1, lenOfCandidate):
                for subset in itertools.combinations(finalCandidate, subsetLen):
                    antecedent = frozenset(subset)
                    confidence = finalCandidateswSupport[finalCandidate]/finalCandidateswSupport[antecedent]
                    if(confidence<confidenceThreshold):
                        continue
                    consequent = finalCandidate - antecedent
                    confidenceDict[antecedent, consequent]=confidence
    t1 = time.clock()
    total = t1-t0
    
    if(displayOption=="f" or displayOption=="a"):
        for k,v in finalCandidateswSupport.items():
            sortedK = list(map(int, k))
            sortedK.sort()
            sortedK = ", ".join(str(elements) for elements in sortedK)
            print(sortedK, "(%.2f)"%(v/numberofTransactions), file = f)

    if(displayOption=="absent"):
        print("Number of strong association rules:", len(confidenceDict), file = f)

    if(displayOption=="r" or displayOption=="a"):
        for k,v in confidenceDict.items():
            ante = list(map(int, k[0]))
            ante.sort()
            ante = ", ".join(str(elements) for elements in ante)
            cons = list(map(int, k[1]))
            cons.sort()
            cons = ", ".join(str(elements) for elements in cons)
            print("%s -> %s (%.2f, %.2f)" %(ante, cons, finalCandidateswSupport[k[0]|k[1]]/numberofTransactions, v), file = f)
    f.close()
    print("Total time taken:", total)

def getItemSetCounts(newCandidates, transactionSets, itemLen):
    """This function returns counts for the candidate itemsets
    
    Arguments:
        newCandidates {[list]} -- [list of all generated candidate itemsets]
        transactionSets {[list]} -- [list of all transactions in database]
        itemLen {[int]} -- [length of candidate itemsets]
    """

    for transaction in transactionSets:
        #Looking for subsets of the transaction of the same length in the candidate list is much faster
        if(nCr(len(transaction), itemLen)<len(newCandidates)):
            for item in itertools.combinations(transaction, itemLen):
                if frozenset(item) in newCandidates:
                    newCandidates[frozenset(item)]+=1
        else:
            for candidate in newCandidates:
                if candidate.issubset(transaction):
                    newCandidates[candidate]+=1

def generateNextCandidateSet(prunedList):
    """Generate itemsets of k+1 length using k length itemsets.
    Only when first k-1 characters match.
    
    Arguments:
        prunedList {[list]} -- [list of pruned k length itemsets]
    
    Returns:
        [list] -- [list of all k+1 length candidate itemsets]
    """

    getListofKeys = list(prunedList.keys())
    newCandidates = {}
    loopLen = len(getListofKeys)
    tempList = []
    for canSet in prunedList:
        makeSortedList = list(canSet)
        makeSortedList.sort()
        tempList.append(makeSortedList)
    for i in range(loopLen):
        currentSet = tempList[i]
        for j in range(i+1, loopLen):
            if(currentSet[:-1]==tempList[j][:-1]):
                newCandidates[getListofKeys[i]|getListofKeys[j]]=0
    return newCandidates


def calcSupportAndPrune(candidateItems, supportValue):
    """Prunes the candidate itemsets which are below minimum support
    
    Arguments:
        candidateItems {[list]} -- [list of candidate itemsets to be pruned]
        supportValue {[float]} -- [minimum support count]
    
    Returns:
        [list] -- [list of pruned itemsets]
    """

    candidateItems = {k:v for k,v in candidateItems.items() if v>=supportValue}
    return candidateItems

def getAllTransactions(filename):
    """Returns all transactions in the file
    
    Arguments:
        filename {[string]} -- [filename]
    
    Returns:
        [list] -- [list of all transactions]
    """

    try:
        file = open(filename, "r") 
    except FileNotFoundError:
        print(filename, "does not exist")
        exit()
    return file.readlines()

def nCr(n,r):
    """Returns number of all possible combinations
    """

    if n<r:
        return 0
    f = math.factorial
    return f(n) / f(r) / f(n-r)

if __name__ == "__main__":
    main(sys.argv[1:])