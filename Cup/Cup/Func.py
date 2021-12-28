from math import ceil, floor, log10, sqrt, trunc

def sieve_of_eratosthenes(number):
    prime = [True for i in range(number+1)]
    prime[0]=prime[1]=False
    for i in range(2, int(sqrt(number))+1):
        if prime[i]:
            for j in range(i*i, number+1, i):
                prime[j]=False
    return [int(i) for i in range(2, len(prime)) if prime[i]]

def fact(number):
    prime_fact = {}
    while number%2==0:
        if 2 not in prime_fact: prime_fact[2]=1
        else: prime_fact[2]+=1
        number/=2
    for i in range(3, int(sqrt(number))+1, 2):
        while number%i==0:
            if i not in prime_fact: prime_fact[i]=1
            else: prime_fact[i]+=1
            number/=i
    if number>2: prime_fact[number]=1
    return prime_fact

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

def binary_search(array, begin, end, element):
    left = begin
    right = end
    while left <= right:
        mid = left + (right - left) // 2
        if array[mid] == element:
            return mid
        elif array[mid] < element:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def lower_bound(array, begin, end, element):
    low = begin
    high = end
    while low < high:
        mid = low + (high - low) // 2
        if element <= array[mid]:
            high = mid
        else:
            low = mid + 1
    if low < end and array[low] < element:
        low += 1
    return low

def upper_bound(array, begin, end, element):
    low = begin
    high = end
    while low < high:
        mid = low + (high - low) // 2
        if element >= array[mid]:
            low = mid + 1
        else:
            high = mid
    if low < end and array[low] <= element:
        low += 1
    return low

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
   
def logbase(number, value):
    return 10**(log10(number)/value)

def is_prime(number):
    try:
        number = int(number)
    except:
        return False
    if number < 2: return False
    if number < 4: return True
    for i in range(2, int(sqrt(number))+1):
        if number%i==0: return False
    return True

def is_palindrome(string):
    string = str(string)
    if len(string)==1: return True
    for i in range(0, len(string)//2 + 1):
        if string[i] != string[len(string)-i-1]:
            return False
    return True

def only_alpha(string):
    string = str(string)
    for i in string:
        if i>='0' and i<='9':
            return False
    return True

def only_digit(string):
    string = str(string)
    for i in string:
        if (i>='a' and i<='z') or (i>='A' and i<='Z'):
            return False
    return True

def roman_to_int(string):
    string = str(string)

    translations = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000
    }
    for i in string:
        if i not in translations: return -1
    number = 0
    string = string.replace("IV", "IIII").replace("IX", "VIIII")
    string = string.replace("XL", "XXXX").replace("XC", "LXXXX")
    string = string.replace("CD", "CCCC").replace("CM", "DCCCC")
    for char in string:
        number += translations[char]
    return number

def int_to_roman(number):
    try:
        number = int(number)
    except:
        return None
    dict = ["M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"]
    nums = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    result = ""
    for letter, n in zip(dict, nums):
        result += letter * int(number / n)
        number %= n
    return result

def morse_code(message, mode):
    MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-'}

    if mode != "encrypt" and mode != "decrypt":
        return None
    elif mode == "encrypt":
        result = ""
        for letter in message:
            if letter != ' ':
                result += MORSE_CODE_DICT[letter] + ' '
            else:
                result += ' '
        return result
    elif mode == "decrypt":
        message += ' '
        result = ""
        citext = ""
        for letter in message:
            if letter != ' ':
                i = 0
                citext += letter
            else:
                i += 1
                if i==2:
                    result += ' '
                else:
                    result += list(MORSE_CODE_DICT.keys())[list(MORSE_CODE_DICT.values()).index(citext)]
                    citext = ""
        return result

def is_square(number):
    try: number = int(number)
    except: return False
    n = int(sqrt(number))
    return n*n == number

def is_cube(number):
    try: number = int(number)
    except: return False
    n = ceil(number**(1/3))
    return n*n*n==number

def digit_sum(number):
    try: number = int(number)
    except: return -1
    sum = 0
    while number!=0:
        sum += number%10
        number//=10
    return sum

def is_decrease(array):
    for i in range(1, len(array)):
        if array[i]>=array[i-1]:
            return False
    return True

def is_increase(array):
    for i in range(1, len(array)):
        if array[i]<=array[i-1]:
            return False
    return True

def is_none_decrease(array):
    for i in range(1, len(array)):
        if array[i]<array[i-1]:
            return False
    return True

def is_none_increase(array):
    for i in range(1, len(array)):
        if array[i]>array[i-1]:
            return False
    return True

def is_unique_array(array):
    for i in range(0, len(array)-1):
        if array[i]==array[i+1]:
            return False
    return True

def is_unique_string(string):
    c = sorted(string)
    for i in range(0, len(c)-1):
        if c[i]==c[i+1]:
            return False
    return True

def frequency(array):
    dict = {}
    for i in array:
        if i not in dict:
            dict[i]=1
        else:
            dict[i]+=1
    return dict



