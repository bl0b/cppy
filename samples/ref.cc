namespace x {
int& foobar();
}
int& some_func() {
    static int toto;
    x::foobar() = toto;
    return toto;
}

void test() {
    some_func() = 42;
}

