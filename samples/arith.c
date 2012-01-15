typedef unsigned int uint;

uint fact(uint n) {
    if(n<=1) {
        return 1;
    }
    return n*fact(n-1);
}

uint fibo(uint n) {
    if(n<=2) {
        return 1;
    }
    return fibo(n-2)+fibo(n-1);
}


