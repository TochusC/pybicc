#include <iostream>

// 扩展欧几里得算法的返回结构体
typedef struct{
    long long d;
    long long x;
    long long y;
}ExtendedGCDResult;

// 扩展欧几里得算法
ExtendedGCDResult extendedGcd(long long a, long long b){
    ExtendedGCDResult result;
    if(b == 0){
        result.d = a;
        result.x = 1;
        result.y = 0;
        return result;
    }
    result = extendedGcd(b, a - a / b * b);

    ExtendedGCDResult temp;
    temp.d = result.d;
    temp.x = result.y;
    temp.y = result.x - a / b * result.y;

    return temp;
}

// 求最大公约数
long long getGCD(long long a, long long b){
    if(b == 0){
        return a;
    }
    return getGCD(b, a - a / b * b);
}

// 求模逆元
long long getModInverse(long long a, long long m){
    if (getGCD(a, m) != 1){
        return -1;
    }
    ExtendedGCDResult result = extendedGcd(a, m);
    long long x = result.x;
    x = x - x / m * m;
    x = x + m;
    x = x - x / m * m;
    return x;
}

bool isPrime[1024];
long long prime[1024];
long long primeNum = 0;

// 筛法求素数
void sieve(long long n){
    for(long long i = 0; i <= n; i++){
        isPrime[i] = true;
    }
    isPrime[0] = isPrime[1] = false;
    for(long long i = 2; i <= n; i++){
        if(isPrime[i]){
            prime[primeNum++] = i;
            for(long long j = i * i; j <= n; j += i){
                isPrime[j] = false;
            }
        }
    }
}

long long encrypt(long long m, long long e, long long n){
    long long c = 1;
    for(long long i = 0; i < e; i++){
        c = (c * m);
        c = c - c / n * n;
    }
    return c;
}

long long decrypt(long long c, long long d, long long n){
    long long m = 1;
    for(long long i = 0; i < d; i++){
        m = (m * c);
        m = m - m / n * n;
    }
    return m;
}

int main(){
    sieve(1024);
    long long p = prime[primeNum - 1];
    long long q = prime[primeNum - 2];
    long long n = p * q;
    long long phi = (p - 1) * (q - 1);

    // 寻找与phi互质的e
    long long e = 0;
    for (e = phi; e >= 1; e--){
        if(getGCD(e, phi) == 1){
            break;
        }
    }

    // 计算d
    long long d = getModInverse(e, phi);

    // 公钥(n, e) 私钥(n, d)

    long long m = 123;
    long long c = encrypt(m, e, n);
    long long m2 = decrypt(c, d, n);

    std::cout << "m2: " << m2 << std::endl;

    return 0;
}