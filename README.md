Tech Hub Kenya Sales Analysis
1. Project Overview
This project analyses Tech Hub Kenya's September 2026 sales data. The company sells phones, laptops, and accessories across five stores.

The aim is to help the finance manager understand:
- Total revenue for the month
- Which products generated the most revenue
- How revenue is split by store and payment method
- Which transactions were worth following up because they were at least KES 50,000
- The typical and largest transaction values
The analysis is written in Python. Tasks 1–7 use Python's standard library, while pandas is used at the end to check the results independently.

2. Tools Used
- Python standard library: csv for reading the file and built-in functions and data structures for cleaning and analysis
- pandas: used only to verify the results on a laptop
- CSV: the format of the original sales export

  3. Data Cleaning Decisions
The CSV contains 50 sales rows. Each row includes a sale ID, date, store, product, quantity, unit price, and payment method.

I chose to repair values only when the intended number was clear. I did not guess missing or unclear values.

| Data issue | Example | Decision | Reason |
|---|---|---|---|
| Extra spaces around a number | ` 18999 ` | Remove surrounding spaces | Spaces do not change the value. |
| Comma used as a thousands separator | `38,999` | Convert to `38999` | The comma is in a valid thousands format. |
| Currency label before a price | `KES 18999` | Convert to `18999` | The currency label is clear and does not change the amount. |
| Quantity written as a word | `two` | Skip the row | The program should not guess or translate an unclear numeric field. |
| Missing quantity | blank | Skip the row | The number of items sold is unknown. |
| Missing or invalid price | blank or `N/A` | Skip the row | Revenue cannot be calculated reliably without a price. |

Other validation rules:
- Quantity must be a positive whole number. A quantity of zero, a negative quantity, or a fraction is not accepted as a count of items.
- Unit price must be greater than zero.
- Negative, non-finite, malformed, or unrecognised numeric values are rejected.
- If quantity or unit price fails validation, the row is skipped and a reason is recorded. Missing values are not replaced with zero because that would distort the revenue.

Rows skipped
Four rows are excluded from the calculations:

| Sale ID | Problem | Why it was skipped |
|---|---|---|
| `S-3006` | Quantity is `two` | The quantity cannot be converted to a number safely. |
| `S-3030` | Unit price is `N/A` | The selling price is unknown. |
| `S-3035` | Quantity is blank | The number of items sold is unknown. |
| `S-3039` | Unit price is blank | The selling price is missing. |

The values 38,999 and KES 18999 are repaired rather than skipped because their numeric meaning is clear.
4. How Revenue Is Calculated
For each valid sale:

Transaction revenue = quantity × unit price

For example, if a customer buys 2 tablets at KES 24,999 each:

2 × 24,999 = KES 49,998

The program calculates revenue for each valid row and adds those amounts to get total revenue. It then groups the same revenue values by product, store, and payment method.

A transaction is considered high-value when its revenue is greater than or equal to KES 50,000. The threshold is inclusive, meaning a transaction worth exactly KES 50,000 would qualify.

For the top-product ranking, revenue is sorted from highest to lowest. If products have the same revenue, their names are sorted alphabetically to break the tie consistently.
5. Results
After applying the cleaning rules above, the program reports:
- Rows read: 50
- Rows included in the analysis: 46
- Rows skipped: 4
- Total revenue: KES 1,310,812.00
- High-value transactions: 5

Top three products by revenue
| Rank | Product | Revenue |
|---:|---|---:|
| 1 | HP 15 Laptop | KES 389,994.00 |
| 2 | Hisense 43in Smart TV | KES 272,993.00 |
| 3 | Lenovo Tab M10 | KES 199,992.00 |

Revenue by store
| Store | Revenue |
|---|---:|
| Kisumu Mega Plaza | KES 449,678.00 |
| Nairobi CBD | KES 331,085.00 |
| Westgate | KES 235,979.00 |
| Mombasa City Mall | KES 154,082.00 |
| Nakuru Westside | KES 139,988.00 |

Revenue by payment method
| Payment method | Revenue |
|---|---:|
| M-Pesa | KES 738,568.00 |
| Cash | KES 304,375.00 |
| Card | KES 267,869.00 |

High-value transactions
| Sale ID | Store | Product | Quantity | Revenue |
|---|---|---|---:|---:|
| `S-3013` | Westgate | Lenovo Tab M10 | 4 | KES 99,996.00 |
| `S-3017` | Kisumu Mega Plaza | Hisense 43in Smart TV | 4 | KES 155,996.00 |
| `S-3022` | Nairobi CBD | HP 15 Laptop | 4 | KES 259,996.00 |
| `S-3036` | Nakuru Westside | Tecno Spark 20 | 4 | KES 53,996.00 |
| `S-3048` | Kisumu Mega Plaza | HP 15 Laptop | 2 | KES 129,998.00 |

These sales are flagged for follow-up because of their value. A high value alone does not mean that a sale has a problem or that payment is outstanding.

Revenue statistics per transaction
| Statistic | Amount |
|---|---:|
| Mean (average) | KES 28,495.91 |
| Median (middle value) | KES 11,097.00 |
| Minimum | KES 1,499.00 |
| Maximum | KES 259,996.00 |

6. Main Functions in sales_analysis.py

Function | What it does |
|---|---|
| `read_sales(path)` | Reads the CSV using `csv.DictReader` and prints the row count and column names. |
| `parse_number(value)` | Cleans and converts numeric text when it can be interpreted safely. |
| `convert_rows(rows)` | Validates quantity and price, calculates revenue for valid rows, and records reasons for skipped rows. |
| `total_revenue(rows)` | Adds the revenue from all valid transactions. |
| `revenue_by(rows, field)` | Groups revenue by product, store, or payment method using a normal dictionary. |
| `top_n(totals, n)` | Returns the highest totals first, with alphabetical tie-breaking. |
| `high_value(rows, threshold)` | Selects transactions that meet or exceed the threshold using a list comprehension. |
| `mean(values)` | Calculates the average transaction revenue. |
| `median(values)` | Calculates the middle transaction revenue after sorting the values. |
| `minimum_maximum(values)` | Finds the smallest and largest transaction revenues without using `min()` or `max()`. |
| `verify_with_pandas(path, my_results)` | Repeats the cleaning and key calculations with pandas and compares the results. |

8. How the pandas Verification Works
   
The Python analysis is completed first. The verification function then reads the original CSV with pandas and applies the same numeric cleaning rules. It creates a valid-row filter using the quantity and unit-price requirements, calculates revenue again, and recomputes the main totals.

It compares these pandas results with the results from the standard-library functions:
- Total revenue
- Revenue by product
- Revenue by store
- Revenue by payment method
- Number of high-value transactions
- Number of clean rows
- Number of skipped rows
Each check prints MATCH if the values agree or MISMATCH if they differ. Numeric totals are compared with a small tolerance to account for floating-point rounding. If there is a mismatch, the output includes both result sets so the difference can be investigated.

The supplied data produces MATCH for all seven checks. This gives an independent check that both approaches apply the same cleaning rules and arrive at the same headline numbers.

9. What I Learned
- Reading and processing CSV files with Python's standard library.
- Cleaning inconsistent numeric values while avoiding unsupported assumptions.
- Using dictionaries, loops, sorting, and comprehensions to summarise business data.
- Writing reusable functions for revenue calculations and descriptive statistics.
- Checking the reliability of my results by comparing a standard-library solution with pandas.
- Explaining data-cleaning decisions so another person can understand and reproduce the analysis.

