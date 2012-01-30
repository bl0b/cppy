namespace x {
    struct a {};
    struct b { ::x::a pouet; };
    struct c { a pouet; b plop; };
}

int main() {
    x::c coin;
    c.plop.pouet;
}

