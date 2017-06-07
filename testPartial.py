# from functools import partial
#
# def add(one,two):
#     return one+two
#
# print(add(11,10))
# partF = partial(add,110)
# print(partF(100))


# import itertools
#
# testAry = [[1,2],[4,5]]
# print(testAry)
# testAry = list(itertools.chain(*testAry))
# print(testAry)

testAry = [1,2,3,4]
newAry = "&".join(map(str,testAry))
print(newAry)
if type(newAry[0]) == int:
    print("Int")
elif type(newAry[0]) == str:
    print("str")
else:
    print("other")

