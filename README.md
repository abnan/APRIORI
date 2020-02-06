# A fast APRIORI implementation in Python

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
