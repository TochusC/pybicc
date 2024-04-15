// Define the knapsack problem and solve it using dynamic programming
int values[10];
int weights[100];

// Define the dynamic programming table
int dp[11][101];

// Solve the knapsack problem using dynamic programming
int knapsack(int n, int capacity) {
    // Initialize the dynamic programming table
    for (int i = 0; i <= n; i++) {
        for (int w = 0; w <= capacity; w++) {
            if (i == 0 || w == 0)
                dp[i][w] = 0;
            else if (weights[i - 1] <= w)
                dp[i][w] = (values[i - 1] + dp[i - 1][w - weights[i - 1]]) > dp[i - 1][w] ?
                           (values[i - 1] + dp[i - 1][w - weights[i - 1]]) : dp[i - 1][w];
            else
                dp[i][w] = dp[i - 1][w];
        }
    }
    return dp[n][capacity];
}

int main() {
    int n;
    int capacity;

    n = 5;
    capacity = 10;

    values[0] = 6;
    values[1] = 10;
    values[2] = 12;
    values[3] = 14;
    values[4] = 18;

    weights[0] = 2;
    weights[1] = 3;
    weights[2] = 4;
    weights[3] = 5;

    int max_value = knapsack(n, capacity);
    write(max_value);

    return 0;
}