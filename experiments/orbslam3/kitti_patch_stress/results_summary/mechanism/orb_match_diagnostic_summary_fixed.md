# Fixed ORB Match Diagnostic Summary

This summary uses patch bounding boxes inferred from clean-vs-attack image differences. It replaces the earlier diagnostic that assumed the patch started at pixel `(0, 0)`.

| Condition | Pairs | Matches mean | Either patch match % mean ± std | Both patch match % mean ± std | Patch area % | Either density ratio mean ± std | Both density ratio mean ± std |
|---|---:|---:|---:|---:|---:|---:|---:|
| clean_reference_top_left_10pct_region | 7 | 2238.0 | 7.02 ± 4.96 | 5.04 ± 4.17 | 10.00 | 0.70 ± 0.50 | 0.50 ± 0.42 |
| black_10pct_top_left | 7 | 2145.3 | 0.09 ± 0.08 | 0.05 ± 0.05 | 10.00 | 0.01 ± 0.01 | 0.00 ± 0.01 |
| checkerboard_5pct_top_left | 7 | 2458.0 | 25.87 ± 6.72 | 25.85 ± 6.72 | 5.02 | 5.16 ± 1.34 | 5.15 ± 1.34 |
| checkerboard_10pct_top_left | 7 | 2576.1 | 38.05 ± 6.67 | 38.03 ± 6.66 | 10.00 | 3.81 ± 0.67 | 3.80 ± 0.67 |
