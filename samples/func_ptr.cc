struct X {
  int f(int) { return 0; }
  static int f(char) { return 0; }
};

/*
int main() {
  int (X::*a)(int) = &X::f;
  int (*b)(int) = &X::f;
}
//*/

