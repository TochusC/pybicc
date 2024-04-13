void change(int *p){
    *p = 16;
    return 0;
}

int main() {
    int i = 3;
    int *p=&i;

    *p = 20;
    write(*p);

    int **z=&p;
    change(*z);

    write(*p);

    return 0;
}