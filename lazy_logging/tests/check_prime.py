# Checks whether a given number is prime or not.
num = 9

if num < 1:
	print(num, "is not a prime number.")
else:
	for i in range(2, num//2):
		if (num % i) == 0:
			print(num, "is not a prime number.")
			break
	else:
		print(num, "is a prime number.")
	
