from math import sqrt

def sieve_of_eratosthenes():
    prime = [True for i in range(n+1)]
    prime[0]=prime[1]=False
    for i in range(2, int(sqrt(n))+1):
        if prime[i]:
            for j in range(i*i, n+1, i):
                prime[j]=False
    return [int(i) for i in range(2, len(prime)) if prime[i]]

def fact(n):
    prime_fact = {}
    while n%2==0:
        if 2 not in prime_fact: prime_fact[2]=1
        else: prime_fact[2]+=1
        n/=2
    for i in range(3, int(sqrt(n))+1, 2):
        while n%i==0:
            if i not in prime_fact: prime_fact[i]=1
            else: prime_fact[i]+=1
            n/=i
    if n>2: prime_fact[n]=1
    return prime_fact

def large_sum(first_number, second_number):
    first_number = str(first_number)
    second_number = str(second_number)
    if len(first_number)> len(second_number):
        first_number, second_number = second_number, first_number
    result = ""
    n1 = len(first_number)
    n2 = len(second_number)
    diff = n2 - n1
    carry = 0
    for i in range(n1-1,-1,-1):
        sum = ((ord(first_number[i])-ord('0')) + int((ord(second_number[i+diff])-ord('0'))) + carry)
        result = result+str(sum%10)
        carry = sum//10
    for i in range(n2-n1-1,-1,-1):
        sum = ((ord(second_number[i])-ord('0'))+carry)
        result = result+str(sum%10)
        carry = sum//10
    if (carry):
        result+str(carry+'0')
    result = result[::-1]
    return result

def nCk(n, k):
    C = [0 for i in range(k+1)]
    C[0]=1
    for i in range(1,n+1):
        j=min(i,k)
        while j>0:
            C[j]=C[j]+C[j-1]
            j-=1
    return C[k]

def nPk(n, k):
    p = 1
    for i in range(k):
        p *= (n-i)
    return p

def divisors(n):
    div = []
    for i in range(1, int(sqrt(n))+1):
        if n%i==0:
            if i*i==n: div.append(i)
            else:
                div.append(i)
                div.append(n//i)
    div.sort()
    return div

def binary_search(array, x):
    array.sort()
    l=0; r = len(array)-1
    while l <= r:
        mid = l + (r - l) // 2
        if array[mid] == x:
            return True
        elif array[mid] < x:
            l = mid + 1
        else:
            r = mid - 1
    return False

def pre_sum(array):
    for i in range(1, len(array)):
        array[i]+=array[i-1]
    return array

def pre_prod(array):
    for i in range(1, len(array)):
        array[i]*=array[i-1]
    return array

def suf_sum(array):
    for i in range(len(array)-2, -1, -1):
        array[i]+=array[i+1]
    return array

def suf_prod(array):
    for i in range(len(array)-2, -1, -1):
        array[i]*=array[i+1]
    return array
   
