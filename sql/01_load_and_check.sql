-- Table: ab  (userid, version, sum_gamerounds, retention_1, retention_7)
-- retention_* stored as 0/1. Runs on DuckDB and SQLite.

-- Q1. Sample size and share per group
SELECT version,
       COUNT(*)                                   AS n_users,
       ROUND(1.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS share
FROM ab
GROUP BY version
ORDER BY version;

-- Q2. Duplicate users / missing values
SELECT COUNT(*) - COUNT(DISTINCT userid) AS duplicate_userids,
       SUM(CASE WHEN version IS NULL OR sum_gamerounds IS NULL
                  OR retention_1 IS NULL OR retention_7 IS NULL THEN 1 ELSE 0 END) AS rows_with_nulls
FROM ab;

-- Q3. Retention by group (primary = retention_7, secondary = retention_1)
SELECT version,
       COUNT(*)                          AS n,
       SUM(retention_1)                  AS ret1_users,
       ROUND(AVG(retention_1), 4)        AS ret1_rate,
       SUM(retention_7)                  AS ret7_users,
       ROUND(AVG(retention_7), 4)        AS ret7_rate
FROM ab
GROUP BY version
ORDER BY version;

-- Q4. Guardrail: game rounds summary
SELECT version,
       ROUND(AVG(sum_gamerounds), 2) AS mean_rounds,
       MAX(sum_gamerounds)           AS max_rounds,
       SUM(CASE WHEN sum_gamerounds = 0 THEN 1 ELSE 0 END)           AS zero_round_users,
       ROUND(AVG(CASE WHEN sum_gamerounds = 0 THEN 1.0 ELSE 0 END),4) AS zero_round_share
FROM ab
GROUP BY version
ORDER BY version;

-- Q5. Top 5 largest round counts (outlier check)
SELECT userid, version, sum_gamerounds
FROM ab
ORDER BY sum_gamerounds DESC
LIMIT 5;

-- Q6. Retention by engagement bucket (CASE WHEN stratification)
SELECT version,
       CASE WHEN sum_gamerounds = 0   THEN '0'
            WHEN sum_gamerounds <= 10 THEN '1-10'
            WHEN sum_gamerounds <= 30 THEN '11-30'
            WHEN sum_gamerounds <= 100 THEN '31-100'
            ELSE '100+' END AS rounds_bucket,
       COUNT(*)                   AS n,
       ROUND(AVG(retention_7), 4) AS ret7_rate
FROM ab
GROUP BY version, rounds_bucket
ORDER BY rounds_bucket, version;
