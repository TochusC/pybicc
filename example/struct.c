typedef struct {
    int x;
    int y;
} Point;

void random_point(Point *p) {
    p->x = 3;
    p->y = 4;
    return 0;
}

int main() {
    Point p;
    random_point(&p);
    return p.x + p.y;
}