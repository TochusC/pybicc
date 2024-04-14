// Extended Euclidean Algorithm
typedef struct{
    long long d;
    long long x;
    long long y;
}ExtendedGCDResult;

// Extended Euclidean Algorithm
ExtendedGCDResult extendedGcd(long long a, long long b){
    ExtendedGCDResult result;
    if(b == 0){
        result.d = a;
        result.x = 1;
        result.y = 0;
        return result;
    }
    result = extendedGcd(b, a % b);

    ExtendedGCDResult temp;
    temp.d = result.d;
    temp.x = result.y;
    temp.y = result.x - a / b * result.y;

    return temp;
}

// solve ax + by = gcd(a, b)
long long getGCD(long long a, long long b){
    if(b == 0){
        return a;
    }
    return getGCD(b, a % b);
}

// solve ax = 1 (mod m)
long long getModInverse(long long a, long long m){
    if (getGCD(a, m) != 1){
        return -1;
    }
    ExtendedGCDResult result = extendedGcd(a, m);
    long long x = result.x;
    return (x % m + m) % m;
}

int isPrime[128];
long long prime[128];
long long primeNum;

// Sieve of Eratosthenes
void sieve(long long n){
    for(long long i = 0; i <= n; i++){
        isPrime[i] = 1;
    }
    isPrime[0] = isPrime[1] = 0;
    for(long long i = 2; i <= n; i++){
        if(isPrime[i] == 1){
            prime[primeNum++] = i;
            for(long long j = i * i; j <= n; j += i){
                isPrime[j] = 0;
            }
        }
    }
}

// Fast Power Encryption and Decryption
long long encrypt(long long m, long long e, long long n){
    long long result = 1;
    long long exp = e;
    long long base = m;
    while(exp > 0){
        if(exp % 2 == 1){
            result = result * base % n;
        }
        base = base * base % n;
        exp /= 2;
    }
    return result;
}

long long decrypt(long long c, long long d, long long n){
   long long result = 1;
    long long exp = d;
    long long base = c;

    while(exp > 0){
        if(exp % 2 == 1){
            result = result * base % n;
        }
        base = base * base % n;
        exp >>= 1;
    }
    return result;
}

int main(){
    primeNum = 0;
    sieve(32);

    long long p = prime[primeNum - 1];
    long long q = prime[primeNum - 2];
    long long n = p * q;
    long long phi = (p - 1) * (q - 1);

    // e
    long long e = 0;
    for (e = phi; e >= 1; e--){
        if(getGCD(e, phi) == 1){
            break;
        }
    }

    // d
    long long d = getModInverse(e, phi);

    // public key, private key
    long long m = 456;
    long long c = encrypt(m, e, n);
    long long m2 = decrypt(c, d, n);

    return m2;
}