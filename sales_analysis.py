"""
Tech Hub Kenya - September 2026 Sales Analysis

Tasks 1-7 use only Python's standard library.
pandas is allowed in task 8, to VERIFY
"""

import csv
import math
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent / "electronics_sales.csv"

# Any sale worth this much or more counts as a "high value" sale
HIGH_VALUE_THRESHOLD = 50000.00


# ---------------------------------------------------------------
# STEP 1: Read the raw data from the CSV file
# ---------------------------------------------------------------
def read_sales(path=DATA_PATH):
    with open(path, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        columns = reader.fieldnames or []

    print(f"Rows read: {len(rows)}")
    print(f"Columns found: {', '.join(columns)}")
    return rows


# ---------------------------------------------------------------
# STEP 2: Clean the numbers (quantity and unit price)
# ---------------------------------------------------------------
def parse_number(value):
    # Turn a messy text value into a number.
    # Returns None if the value is blank, a word, negative or not a real number.
    if value is None:
        return None

    cleaned = str(value).strip()
    if cleaned == "":
        return None

    # If the value starts with "KES", drop the label and keep the amount
    if cleaned.upper().startswith("KES"):
        cleaned = cleaned[3:].strip()

    # Commas are only allowed as thousands separators
    if "," in cleaned:
        pieces = cleaned.split(",")
        first_ok = 1 <= len(pieces[0]) <= 3 and pieces[0].isdigit()
        rest_ok = all(len(p) == 3 and p.isdigit() for p in pieces[1:])
        if not (first_ok and rest_ok):
            return None
        cleaned = "".join(pieces)

    # Try to convert to a float, anything that fails is treated as invalid
    try:
        number = float(cleaned)
    except ValueError:
        return None

    # Reject nan / inf and negative numbers
    if not math.isfinite(number) or number < 0:
        return None

    return number


def convert_rows(rows):
    # Go through every row, keep the good ones and set aside the bad ones
    clean_rows = []
    skipped_rows = []

    for original in rows:
        row = dict(original)
        quantity = parse_number(row.get("quantity", ""))
        unit_price = parse_number(row.get("unit_price_kes", ""))
        reasons = []

        # Check the quantity
        if quantity is None:
            reasons.append(f"invalid quantity {row.get('quantity', '')!r}")
        elif quantity <= 0 or not quantity.is_integer():
            reasons.append(f"quantity must be a positive whole number (got {row.get('quantity', '')!r})")

        # Check the unit price
        if unit_price is None:
            reasons.append(f"invalid unit_price_kes {row.get('unit_price_kes', '')!r}")
        elif unit_price <= 0:
            reasons.append(f"unit price must be greater than zero (got {row.get('unit_price_kes', '')!r})")

        # If anything was wrong, skip the row but remember why
        if reasons:
            bad_row = dict(original)
            bad_row["skip_reason"] = "; ".join(reasons)
            skipped_rows.append(bad_row)
            continue

        # Otherwise store the cleaned values and work out the revenue
        row["quantity"] = int(quantity)
        row["unit_price_kes"] = float(unit_price)
        row["revenue"] = row["quantity"] * row["unit_price_kes"]
        clean_rows.append(row)

    return clean_rows, skipped_rows


# ---------------------------------------------------------------
# STEP 3: Total revenue
# ---------------------------------------------------------------
def total_revenue(rows):
    # Revenue for one sale = quantity x unit price, then add them all up
    total = 0.0
    for row in rows:
        total += row["quantity"] * row["unit_price_kes"]
    return total


# ---------------------------------------------------------------
# STEP 4: Revenue grouped by product, store and payment method
# ---------------------------------------------------------------
def revenue_by(rows, field):
    # Adds up revenue for each unique value in the given column
    totals = {}
    for row in rows:
        key = str(row.get(field, "")).strip()
        if key not in totals:
            totals[key] = 0.0
        totals[key] += row["revenue"]
    return totals


# ---------------------------------------------------------------
# STEP 5: Top performers
# ---------------------------------------------------------------
def top_n(totals, n=3):
    # Sort highest revenue first. If two are tied, sort by name
    if n < 0:
        raise ValueError("n must be zero or greater")
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:n]


# ---------------------------------------------------------------
# STEP 6: High value sales
# ---------------------------------------------------------------
def high_value(rows, threshold):
    # Keep only the sales that reach the threshold
    big = []
    for row in rows:
        if row["revenue"] >= threshold:
            big.append(row)
    return big


# ---------------------------------------------------------------
# STEP 7: Statistics (written by hand, no statistics module)
# ---------------------------------------------------------------
def mean(values):
    if len(values) == 0:
        raise ValueError("mean() requires at least one value")
    return sum(values) / len(values)


def median(values):
    if len(values) == 0:
        raise ValueError("median() requires at least one value")

    ordered = sorted(values)
    middle = len(ordered) // 2

    # Odd count: take the middle one. Even count: average the two middle ones.
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def minimum_maximum(values):
    # Find the smallest and largest value without using min() or max()
    if len(values) == 0:
        raise ValueError("minimum_maximum() requires at least one value")

    smallest = values[0]
    largest = values[0]
    for value in values[1:]:
        if value < smallest:
            smallest = value
        if value > largest:
            largest = value
    return smallest, largest


# ---------------------------------------------------------------
# EXTRA STEP: Double check my results with pandas
# ---------------------------------------------------------------
def verify_with_pandas(path, my_results):
    # pandas is imported here so the rest of the script works without it
    try:
        import pandas as pd
    except ImportError:
        print("\nPandas verification skipped: pandas is not installed in this environment.")
        print("Install pandas on your laptop with: python -m pip install pandas")
        return

    # Read everything as text so pandas does not guess the data types
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)

    # Reuse my own cleaning function so both methods follow the same rules
    frame["quantity_num"] = frame["quantity"].map(parse_number)
    frame["price_num"] = frame["unit_price_kes"].map(parse_number)

    # Keep only the valid rows
    valid = (
        frame["quantity_num"].notna()
        & frame["price_num"].notna()
        & (frame["quantity_num"] > 0)
        & (frame["quantity_num"] % 1 == 0)
        & (frame["price_num"] > 0)
    )
    clean = frame.loc[valid].copy()
    clean["revenue"] = clean["quantity_num"] * clean["price_num"]

    # Recalculate the headline numbers using pandas
    checks = {
        "total_revenue": float(clean["revenue"].sum()),
        "product_revenue": clean.groupby("product")["revenue"].sum().to_dict(),
        "store_revenue": clean.groupby("store")["revenue"].sum().to_dict(),
        "payment_revenue": clean.groupby("payment_method")["revenue"].sum().to_dict(),
        "high_value_count": int((clean["revenue"] >= HIGH_VALUE_THRESHOLD).sum()),
        "clean_row_count": int(len(clean)),
        "skipped_row_count": int(len(frame) - len(clean)),
    }

    # Small helper: two numbers match if they are equal (ignoring tiny rounding)
    def same_number(a, b):
        return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=0.01)

    # Small helper: two dictionaries match if they have the same keys and values
    def same_dict(a, b):
        if a.keys() != b.keys():
            return False
        for key in b:
            if not same_number(a[key], b[key]):
                return False
        return True

    # Compare my answers with the pandas answers
    comparisons = [
        ("Total revenue", same_number(my_results["total_revenue"], checks["total_revenue"])),
        ("Product revenue breakdown", same_dict(my_results["product_revenue"], checks["product_revenue"])),
        ("Store revenue breakdown", same_dict(my_results["store_revenue"], checks["store_revenue"])),
        ("Payment method revenue breakdown", same_dict(my_results["payment_revenue"], checks["payment_revenue"])),
        ("High-value transaction count", my_results["high_value_count"] == checks["high_value_count"]),
        ("Clean row count", my_results["clean_row_count"] == checks["clean_row_count"]),
        ("Skipped row count", my_results["skipped_row_count"] == checks["skipped_row_count"]),
    ]

    # Print MATCH or MISMATCH for each check
    print("\nPandas verification:")
    for label, matched in comparisons:
        if matched:
            print(f"MATCH - {label}")
        else:
            print(f"MISMATCH - {label}")
            print("  Python result:", my_results)
            print("  pandas result:", checks)


# ---------------------------------------------------------------
# MAIN: run all the steps in order and print the results
# ---------------------------------------------------------------
def main():
    # Step 1: read the file
    raw_rows = read_sales(DATA_PATH)

    # Step 2: clean the rows and report the ones we had to skip
    rows, skipped = convert_rows(raw_rows)
    print(f"\nClean rows: {len(rows)}")
    print(f"Skipped rows: {len(skipped)}")
    if skipped:
        print("\nSkipped sales and reasons:")
        for row in skipped:
            print(f"  {row.get('sale_id', 'Unknown ID')}: {row['skip_reason']}")

    # Steps 3 and 4: totals and groupings
    total = total_revenue(rows)
    products = revenue_by(rows, "product")
    stores = revenue_by(rows, "store")
    payments = revenue_by(rows, "payment_method")

    # Step 6: find the high value sales and count them per store
    big_sales = high_value(rows, HIGH_VALUE_THRESHOLD)
    store_high_counts = {}
    for store in stores:
        count = 0
        for sale in big_sales:
            if sale["store"] == store:
                count += 1
        store_high_counts[store] = count

    # Step 7: statistics on the revenue of each transaction
    revenues = [row["revenue"] for row in rows]
    low, high = minimum_maximum(revenues)

    # Print: total revenue
    print(f"\nTOTAL REVENUE: KES {total:,.2f}")

    # Print: every product, highest first
    print("\nRevenue by product (highest first):")
    for product, revenue in top_n(products, len(products)):
        print(f"  {product}: KES {revenue:,.2f}")

    # Print: top 3 products (Step 5)
    print("\nTop 3 products:")
    for product, revenue in top_n(products, 3):
        print(f"  {product}: KES {revenue:,.2f}")

    # Print: revenue by store, highest first
    print("\nRevenue by store:")
    for store, revenue in top_n(stores, len(stores)):
        print(f"  {store}: KES {revenue:,.2f}")

    # Print: revenue by payment method, highest first
    print("\nRevenue by payment method:")
    for method, revenue in top_n(payments, len(payments)):
        print(f"  {method}: KES {revenue:,.2f}")

    # Print: the list of high value sales
    print(f"\nHigh-value sales (revenue >= KES {HIGH_VALUE_THRESHOLD:,.2f}):")
    for sale in big_sales:
        print(f"  {sale['sale_id']} | {sale['sale_date']} | {sale['store']} | "
              f"{sale['product']} | qty {sale['quantity']} | KES {sale['revenue']:,.2f}")

    # Print: how many high value sales each store made
    print("\nHigh-value sales count by store:")
    for store, count in store_high_counts.items():
        print(f"  {store}: {count}")

    # Print: the statistics
    print("\nPer-transaction revenue statistics:")
    print(f"  Mean: KES {mean(revenues):,.2f}")
    print(f"  Median: KES {median(revenues):,.2f}")
    print(f"  Minimum: KES {low:,.2f}")
    print(f"  Maximum: KES {high:,.2f}")

    # Extra step: bundle my results and check them against pandas
    my_results = {
        "total_revenue": total,
        "product_revenue": products,
        "store_revenue": stores,
        "payment_revenue": payments,
        "high_value_count": len(big_sales),
        "clean_row_count": len(rows),
        "skipped_row_count": len(skipped),
    }
    verify_with_pandas(DATA_PATH, my_results)


# Only run main() when this file is run directly
if __name__ == "__main__":
    main()
