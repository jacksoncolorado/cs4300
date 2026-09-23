# if statements, for loops, while loops

# return pos, neg, or zero for given number
# if statement function
def classify_number(number):
    if number > 0:
        return "positive"
    elif number < 0:
        return "negative"
    else:
        return "zero"


# function to confirm if number is prime (True, False otherwise)
# prim is only divisible eby 1 and itself
# for loop
def is_prime(number):
    # only prime even!
    if number < 2:
        return False
    # check divisors up to the square root → **0.5
    for divisor in range(2, int(number**0.5) + 1):
        # if 0, that means it was a factor besides the number and 1..
        if number % divisor == 0:
            return False
    return True


# get first 10 primes
# for loop 
def first_n_primes(count=10):
    primes = []
    for candidate in range(2, 10000):
        # break when list fills...
        if len(primes) >= count:
            break
        # add it to list
        if is_prime(candidate):
            primes.append(candidate)
    return primes

# sum 1 to 100
# while
def sum_to(limit=100):
    total = 0
    current = 1
    while current <= limit:
        total += current # append new sum
        current += 1.  # increment
    return total


if __name__ == "__main__":
    print(classify_number(5))
    print(classify_number(-5))
    print(classify_number(0))
    print(first_n_primes())
    print(sum_to())