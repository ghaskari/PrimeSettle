import pandas as pd
from typing import List, Tuple


def calculate_balances(transactions: List[Tuple[str, str, float]]) -> pd.DataFrame:
    """
    Input:
        [("A", "B", 100), ("B", "C", 50)]
    Output:
        DataFrame with final balances
    """

    df = pd.DataFrame(transactions, columns=["Debtor", "Creditor", "Amount"])

    people = pd.unique(df[["Debtor", "Creditor"]].values.ravel())
    balance = pd.Series(0.0, index=people)

    for _, row in df.iterrows():
        balance[row["Debtor"]] -= row["Amount"]
        balance[row["Creditor"]] += row["Amount"]

    df_balance = balance.reset_index()
    df_balance.columns = ["Name", "FinalBalance"]

    return df_balance


def calculate_settlements(df_balance: pd.DataFrame) -> pd.DataFrame:
    """
    Converts balances into minimal settlement payments
    """

    balance = pd.Series(
        df_balance["FinalBalance"].values,
        index=df_balance["Name"]
    )

    debtors = balance[balance < 0].abs()
    creditors = balance[balance > 0]

    settlements = []

    for debtor, debt_amount in debtors.items():
        for creditor in creditors.index:
            if debt_amount <= 0:
                break
            if creditors[creditor] <= 0:
                continue

            pay = min(debt_amount, creditors[creditor])

            settlements.append({
                "From": debtor,
                "To": creditor,
                "Amount": round(pay, 2)
            })

            debt_amount -= pay
            creditors[creditor] -= pay

    return pd.DataFrame(settlements)


def save_outputs(balance_df: pd.DataFrame, settlement_df: pd.DataFrame):
    balance_df.to_csv("final_balances.csv", index=False)
    settlement_df.to_csv("final_settlements.csv", index=False)
