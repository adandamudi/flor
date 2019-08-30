import random 

# Static analysis on this test file should result in multiple exprs being logged.

################# Example 1 #####################
a = random.randint(0, 9)
a = (lambda x, y: random.randint(x,y) + 1)
a += random.randint(0, 9)

################# Example 2 #####################
a = random.randint(random.randint(0, 9), 9)
b = foo(foo(0,9), 9)

################# Example 3 #####################
def foo(x, y):
	print("hello")
if (random.randint(0,9) < 5):
	print("hello world")
a = 0 + 5 + 10
if (a < 50):
	print("hello world")
