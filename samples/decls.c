namespace a {
    int some_func();
    int some_func() {}
}

typedef unsigned long size_t;

void some_proc(int x, size_t pouet);
void some_proc(int x, size_t pouet) {
    int y = x;
    int z = pouet;
    int u = y+z;
    int r = 4*32;
    int t = ((size_t)x)*pouet;
    int v = z+t+y;
}

void some_proc() {}
void some_proc(float x) {}

void test() {
    some_proc(4, (unsigned int)25);
}

