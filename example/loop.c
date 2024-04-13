int main() {
    int i;
    for (i = 0; i < 10; i++) {
        if (i == 5) {
            break;
        }
    }
    while (i > 0) {
        i = i - 1;
        if (i == 3) {
            continue;
            i *= -2;
        }
    }
    write(i);
    return 0;
}