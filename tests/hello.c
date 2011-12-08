
int a(int p1, int p2) {
    return p1;
}

int b(int p3, int p4) {
    return p4;
}

int c(int p5, int p6) {
    return a(a(p5, p6), b(p5, p6));
}


int main(int argc, char**argv) {
    printf("hello, world!\n");
    for(int i=0;i<10;++i) {
        printf("%i\n", i*i+i-1);
    }
    return 0;
}

