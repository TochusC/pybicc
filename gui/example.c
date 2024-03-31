int main() {
    int x=3;
    int y=5;
    int i;
    for(i = 0; i <= 100; i = i + 1){
        x = x + 1;
        y = y + 1;
    }
    if(y > x){
        *(&x+8)=7; return y;
    }
    else{
        int *p=&i; int **z=&p; return **z;
    }
}