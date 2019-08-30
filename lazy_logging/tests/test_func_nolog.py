import random 

# Static analysis on this test file should result in nothing having to be logged.

################# Example 1 #####################
for i in range(a, b):
	print("hello world")

################# Example 2 #####################
def hello():
	return 1

a = hello()
x = ["hello", "hi", "goodbye"]
del x[0], x[0]

################# Example 3 #####################
def foo(a, b, c):
	return a + b + c

foo(0, b=2, c=3)
foo(0, c=3, b=2)
