def unique_paths(n, m):
    # Create a 2D array to store intermediate results
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    # print(dp)
    # Base case: There is only one way to reach each cell in the first row and first column
    for i in range(n + 1):
        dp[i][0] = 1
    # print(dp)
    for j in range(m + 1):
        dp[0][j] = 1
    print(dp)
    # Fill the dp array using the recurrence relation
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    print(dp)
    # The result is stored in the top right corner of the dp array
    return dp[n][m]

# Example usage:
n = 2
m = 2
result = unique_paths(n, m)
print(f"The number of unique minimum distance paths from (0, 0) to ({n}, {m}) is: {result}")
