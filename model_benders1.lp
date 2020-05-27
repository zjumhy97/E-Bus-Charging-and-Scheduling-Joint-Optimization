\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  7 y[0] + 7 y[1] + 7 y[2] + 7 y[3] + 7 y[4] + z
Subject To
 R0: - 8 y[0] - 5 y[3] - 3 y[4] <= -8
 R1: - 3 y[1] - 5 y[2] - 5 y[3] - 3 y[4] <= -8
 R2: - 5 y[3] - 3 y[4] - z <= -16
Bounds
Binaries
 y[0] y[1] y[2] y[3] y[4]
End
