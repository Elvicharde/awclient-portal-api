from app.schemas.report_schema import SacsInput, TccInput


def calculate_sacs_totals(sacs: SacsInput, is_married: bool) -> dict[str, float]:
    client_2_inflow = sacs.client_2_quarterly_inflow or 0
    client_2_expense = sacs.client_2_quarterly_expense or 0
    total_inflow = sacs.client_1_quarterly_inflow + (client_2_inflow if is_married else 0)
    total_outflow = sacs.client_1_quarterly_expense + (client_2_expense if is_married else 0)
    monthly_expenses = total_outflow / 3
    private_reserve_target = (6 * monthly_expenses) + sacs.insurance_deductible_total

    return {
        "total_inflow": total_inflow,
        "total_outflow": total_outflow,
        "excess": total_inflow - total_outflow,
        "insurance_deductible_total": sacs.insurance_deductible_total,
        "private_reserve_balance": sacs.private_reserve_balance,
        "private_reserve_target": private_reserve_target,
        "monthly_expenses": monthly_expenses,
    }


def calculate_tcc_totals(tcc: TccInput, is_married: bool) -> dict[str, float]:
    client_1_retirement_total = _sum_values(tcc.client_1_retirement_balances)
    client_2_retirement_total = _sum_values(tcc.client_2_retirement_balances) if is_married else 0
    non_retirement_total = _sum_values(tcc.non_retirement_balances)
    trust_total = tcc.trust_value
    liabilities_total = _sum_values(tcc.liability_balances)

    return {
        "client_1_retirement_total": client_1_retirement_total,
        "client_2_retirement_total": client_2_retirement_total,
        "non_retirement_total": non_retirement_total,
        "trust_total": trust_total,
        "grand_total_net_worth": (
            client_1_retirement_total
            + client_2_retirement_total
            + non_retirement_total
            + trust_total
        ),
        "liabilities_total": liabilities_total,
    }


def _sum_values(values: dict[str, float]) -> float:
    return sum(values.values())
