int& some_func();
int& some_func() {
    static int toto;
    return toto;
}

void test() {
    some_func() = 42;
}

