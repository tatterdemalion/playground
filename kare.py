char = '*'


def square(n):
    print(n * char)
    for i in range(n - 2):
        print(char + ((n - 2) * ' ') + char)
    print(n * char)

square(10)


def fill(text, total_fill):
    fill = total_fill - len(text)
    print(text + fill * char)

fill('can', 10)
fill('mustafa', 10)
fill('canmustafaozdemir', 5)


def find_min_nsquared(alist):
    the_min = alist[0]
    for i in alist:
        for j in alist:
            if i > j:
                the_min = j
    return the_min


def find_min_linear(alist):
    the_min = alist[0]
    for i in alist:
        if the_min > i:
            the_min = i
    return the_min

alist = [10, 90, 3, 11, 2]
print(find_min_nsquared(alist))
print(find_min_linear(alist))


def fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(10))
