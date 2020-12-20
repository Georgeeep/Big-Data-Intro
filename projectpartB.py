import json
import re
import csv
import math
import hyperloglog
from probables import (CountMinSketch)
from pympler import asizeof

# *********INITS**********************************
Uniqueuserlist = []
Uniquehashlist = []

Csvnumber = int(input('number of csv files to use (1 or 2 are accepted):'))
if Csvnumber > 2 or Csvnumber < 1:
    print('please select a value of either 1 or 2')
    exit()
UserChoice = int(input('To use ids press 1, to use mention names press 2, to use mention handles press 3:'))
cms = CountMinSketch(width=10000, depth=5)
cmshash = CountMinSketch(width=10000, depth=5)
hll = hyperloglog.HyperLogLog(0.05)
hllhash = hyperloglog.HyperLogLog(0.05)
filenum = 0
Userdict = {}
Hashdict = {}
datapointcount = 0
totalhitters = int(input('enter the number of heavyhitters to track and compare:'))
heavyhitters = [0 for i in range(totalhitters)]
trueposition = -1
truehashposition = -1
countnum = 0
prevposition = totalhitters - 1
prevhashposition = totalhitters - 1
heavyhittersval = [0 for i in range(totalhitters)]
heavyhashhittersval = [0 for i in range(totalhitters)]
heavyhashhitters = [0 for i in range(totalhitters)]
exists = 0
Uniqueusers = 0
Uniquehash = 0
totalfiles = 46
Uniquedictusers = {}
Uniquedicthash = {}
sumdiff = 0
sumdiffhash = 0
sumsquareddiff = 0
sumsquareddiffhash = 0
# ******************FILE READING********************
while filenum < totalfiles:
    filenumstr = str(filenum)
    filename = 'tweets.json' + '.' + filenumstr  # loop through files
    with open(filename, encoding="utf-8") as f:
        for line in f:  # loop through lines

            newline = json.loads(line)

            if UserChoice == 3:
                # **********************************MENTIONHANDLE-VERSION*******************************************************
                textuser = str(newline['text'])
                testlist = re.search(r'^(RT @\w+|@\w+)', textuser)  # search for words that start with @ or rt
                if testlist:
                    users = testlist.group()
                    if users[0] == 'R':
                        users = users[3:]
                finalusers = users[1:]
            # ***********************************id-VERSION*************************************************
            elif UserChoice == 1:
                users = str(newline['user']['id'])
                finalusers = users



            # ***********************************Name-Version************************************************
            elif UserChoice == 2:
                users = str(newline['user']['name'])
                finalusers = users

            # **************************printing per 10000***********************************************
            if countnum == 1000:  # RESULT EVERY 1000
                result = list(zip(heavyhitters, heavyhittersval))
                print(result)
                countnum = 0
                resulthash = list(zip(heavyhashhitters, heavyhashhittersval))
                print(resulthash)

            # **************************ADDING TO DICTIONARIES***********************************************

            if finalusers not in Userdict:
                Userdict[finalusers] = 1
                Uniqueusers += 1  # Q4
                Uniqueuserlist.append(finalusers)
            else:
                Userdict[finalusers] = Userdict[finalusers] + 1
            if finalusers in heavyhitters:
                trueposition = heavyhitters.index(finalusers)

            cms.add(finalusers)
            hll.add(finalusers)
            currposition = 0
            out = 0
            # ****************************RANKING IN ORDER TOP X********************************************
            while currposition < totalhitters and out == 0:  # loop through all values until the length of the list
                if Userdict[finalusers] > heavyhittersval[currposition]:

                    while prevposition > currposition:  # loop through values from last to first

                        if trueposition != -1:  # test to see if key already exists in list
                            if prevposition > trueposition:
                                prevposition = trueposition  # set prevposition as trueposition previous values dont need to be iterated.

                                continue

                            heavyhitters[prevposition] = heavyhitters[
                                prevposition - 1]  # move all values down for key list and value list
                            heavyhittersval[prevposition] = heavyhittersval[prevposition - 1]

                        if currposition > trueposition:  # case where currposition passes its old position
                            prevposition = currposition
                            heavyhitters[prevposition] = heavyhitters[prevposition - 1]
                            heavyhittersval[prevposition] = heavyhittersval[prevposition - 1]
                        prevposition -= 1

                    heavyhitters[currposition] = finalusers
                    heavyhittersval[currposition] = Userdict[finalusers]
                    prevposition = totalhitters - 1
                    currposition = 0
                    out = 1
                    continue
                currposition += 1
            currposition = 0

            trueposition = -1
            # ***********************************Hashtag search******************************************
            texthash = str(newline['text'])
            hashs = re.findall(r'#\w+', texthash)  # search for words that start with #
            # **************************ADDING TO DICTIONARIES***********************************************
            for items in hashs:
                finalhash = items[1:]  # remove the #

                if finalhash not in Hashdict:  # same as before
                    Hashdict[finalhash] = 1
                    Uniquehash += 1  # Q4
                    Uniquehashlist.append(finalusers)
                else:
                    Hashdict[finalhash] = Hashdict[finalhash] + 1
                if finalhash in heavyhashhitters:
                    truehashposition = heavyhashhitters.index(finalhash)
                cmshash.add(finalhash)
                hllhash.add(finalhash)
                currhashposition = 0
                hashout = 0
                # ****************************RANKING IN ORDER TOP X********************************************
                while currhashposition < totalhitters and hashout == 0:
                    if finalhash == []:
                        continue
                    if Hashdict[finalhash] > heavyhashhittersval[currhashposition]:

                        while prevhashposition > currhashposition:

                            if truehashposition != -1:
                                if prevhashposition > truehashposition:
                                    prevhashposition = truehashposition

                                    continue

                                heavyhashhitters[prevhashposition] = heavyhashhitters[prevhashposition - 1]
                                heavyhashhittersval[prevhashposition] = heavyhashhittersval[prevhashposition - 1]

                            if currhashposition > trueposition:
                                prevhashposition = currhashposition
                                heavyhashhitters[prevhashposition] = heavyhashhittersval[prevhashposition - 1]
                                heavyhashhittersval[prevhashposition] = heavyhashhittersval[prevhashposition - 1]
                            prevhashposition -= 1

                        heavyhashhitters[currhashposition] = finalhash
                        heavyhashhittersval[currhashposition] = Hashdict[finalhash]
                        prevhashposition = totalhitters - 1
                        currhashposition = 0
                        hashout = 1
                        continue
                    currhashposition += 1
                currhashposition = 0

                truehashposition = -1
            countnum += 1
    filenum += 1
    print(filename)

# ****************************PRINTING RESULTS*********************************
print('Name:Exact/approx counters')
for k in heavyhitters:
    Difference = int(cms.check(k)) - int(Userdict[k])
    sumdiff = sumdiff + Difference
    sumsquareddiff = sumsquareddiff + (Difference ** 2)
    print('{0}: {1:3d}/{2} '.format(k, Userdict[k], cms.check(k)))
print('\n')
print('mse for users=', sumsquareddiff / totalhitters)
print('mae for users =', sumdiff / totalhitters)

print('sizeofUserDict=', asizeof.asizeof(Userdict))
print('sizeofcms=', asizeof.asizeof(cms))
print('Unique Users=', Uniqueusers)
print('Estimated Unique Users: {0}'.format(math.ceil(hll.card())))
print('size of unique users:', asizeof.asizeof(Uniqueusers))
print('size of estimated unique users:', asizeof.asizeof(hll.card()))

print('Name:Exact/approx counters for hashtags')
print('\n')
print('\n')
for k in heavyhashhitters:
    Differencehash = int(cmshash.check(k)) - int(Hashdict[k])
    sumdiffhash = sumdiffhash + Differencehash
    sumsquareddiffhash = sumsquareddiffhash + (Differencehash ** 2)
    print('{0}:1 {1:3d}/{2} '.format(k, Hashdict[k], cmshash.check(k)))
print('\n')
print('mae for hashtags =', sumdiffhash / totalhitters)
print('mse for users=', sumsquareddiffhash / totalhitters)
print('size of HashDict=', asizeof.asizeof(Hashdict))
print('size of hashtag cms=', asizeof.asizeof(cmshash))
print('Unique hashtags=', Uniquehash)
print('Estimated Unique hashtags: {0}'.format(math.ceil(hllhash.card())))
print('size of unique hashtags:', asizeof.asizeof(Uniquehash))
print('size of estimated unique hashtags:', asizeof.asizeof(hllhash.card()))
print('size of hllhash=', asizeof.asizeof(hllhash))
print('size of hll=', asizeof.asizeof(hll))
print('uniquehashlist,uniqueuserlist', len(Uniquehashlist), len(Uniqueuserlist))
print('size=hashlist,userlist', asizeof.asizeof(Uniquehashlist), asizeof.asizeof(Uniqueuserlist))

cms.export('cms.csv')
cmshash.export('hashcms.csv')

if Csvnumber == 2:
    csvfile = open('user-counter.csv', 'w+', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_ALL)
    writer.writerow('Users')
    for key, value in Userdict.items():
        writer.writerow([key, value])
    csvfile.close

    csvfile = open('Hash-counter.csv', 'w+', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_ALL)
    writer.writerow('Hashtags')
    for key, value in Hashdict.items():
        writer.writerow([key, value])
    csvfile.close
elif Csvnumber == 1:
    csvfile = open('all-counter.csv', 'w+', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_ALL)
    writer.writerow('Users')
    for key, value in Userdict.items():
        writer.writerow([key, value])
    writer.writerow('Hashtags')
    for key, value in Hashdict.items():
        writer.writerow([key, value])
        csvfile.close
