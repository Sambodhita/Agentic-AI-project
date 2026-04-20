"""
tools.py — Custom tools for Legal Assistant LangGraph Agent
Tools: deadline_calculator, risk_scorer, legal_math
"""

import math
from datetime import datetime, timedelta
from langchain_core.tools import tool


# TOOL 1: Contract Deadline Calculator
@tool
def deadline_calculator(
    contract_start_date: str,
    duration_value: int,
    duration_unit: str,
    notice_period_days: int = 30
) -> str:
    """
    Calculate contract deadlines, expiry dates, and notice windows.

    Args:
        contract_start_date: Contract start date in YYYY-MM-DD format.
        duration_value: Numeric duration of the contract.
        duration_unit: Unit of duration — 'days', 'months', or 'years'.
        notice_period_days: Notice period in days required before termination (default 30).

    Returns:
        A structured summary of all key contract dates and deadlines.
    """
    try:
        start = datetime.strptime(contract_start_date, "%Y-%m-%d")
    except ValueError:
        return "Error: Invalid date format. Please use YYYY-MM-DD (e.g., 2026-01-15)."

    # Calculate end date
    if duration_unit.lower() == "days":
        end = start + timedelta(days=duration_value)
    elif duration_unit.lower() == "months":
        # Add months properly
        month = start.month + duration_value
        year = start.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        day = min(start.day, [31,29 if year%4==0 else 28,31,30,31,30,31,31,30,31,30,31][month-1])
        end = start.replace(year=year, month=month, day=day)
    elif duration_unit.lower() == "years":
        try:
            end = start.replace(year=start.year + duration_value)
        except ValueError:
            end = start + timedelta(days=365 * duration_value)
    else:
        return "Error: duration_unit must be 'days', 'months', or 'years'."

    today = datetime.today()
    days_remaining = (end - today).days
    notice_deadline = end - timedelta(days=notice_period_days)
    days_to_notice = (notice_deadline - today).days

    status = "ACTIVE" if today < end else "EXPIRED"
    notice_status = "⚠️ NOTICE DEADLINE PASSED" if days_to_notice < 0 else (
        "🔴 NOTICE WINDOW OPEN - Act immediately" if days_to_notice < 14 else
        "🟡 Notice window approaching" if days_to_notice < 60 else
        "🟢 Adequate time remaining"
    )

    return f"""
━━━ CONTRACT DEADLINE ANALYSIS ━━━

📅 Contract Start:      {start.strftime('%B %d, %Y')}
📅 Contract End:        {end.strftime('%B %d, %Y')}
📊 Status:              {status}
⏳ Days Remaining:      {days_remaining} days {"(contract has expired)" if days_remaining < 0 else ""}

🔔 Notice Period:       {notice_period_days} days
📅 Send Notice By:      {notice_deadline.strftime('%B %d, %Y')}
⚡ Notice Status:       {notice_status} ({abs(days_to_notice)} days {"ago" if days_to_notice < 0 else "away"})

💡 Recommendation:
{"   ✅ You're well within the contract period. Set a calendar reminder for the notice deadline." if days_remaining > 60 else ""}
{"   ⚠️ Contract ends within 60 days. Consider whether to renew or exercise notice." if 0 < days_remaining <= 60 else ""}
{"   🔴 Contract has EXPIRED. Ensure obligations have been fulfilled and confirm no auto-renewal." if days_remaining < 0 else ""}
"""

# TOOL 2: Contract Risk Scorer

@tool
def risk_scorer(clauses_list: str) -> str:
    """
    Score a list of contract clauses for legal risk level.

    Args:
        clauses_list: A comma-separated or newline-separated list of clause descriptions
                      or clause names from a contract. Examples: 
                      "unlimited liability, no governing law clause, 3-year non-compete worldwide, 
                      automatic renewal, no force majeure, mutual NDA, 30-day notice period"

    Returns:
        A detailed risk assessment with scores for each clause and an overall risk score.
    """
    # Risk pattern database
    HIGH_RISK_PATTERNS = [
        ("unlimited liability", "No cap on damages exposes you to catastrophic financial risk"),
        ("unlimited indemnif", "Indemnifying all possible losses with no ceiling is extremely dangerous"),
        ("perpetual", "Perpetual obligations with no end date trap you indefinitely"),
        ("irrevocable", "Irrevocable grants cannot be undone even under extreme circumstances"),
        ("no governing law", "Without a specified governing law, contract interpretation is unpredictable"),
        ("no termination", "No ability to exit the contract regardless of circumstances"),
        ("automatic renewal", "Auto-renewal without notice can lock you in for another full term"),
        ("waive all rights", "Waiving legal rights removes important protections"),
        ("no force majeure", "Without force majeure, you are liable even for unforeseeable events"),
        ("unilateral modification", "Other party can change terms without your consent"),
        ("no cure period", "Party can terminate immediately on first breach without chance to remedy"),
        ("all ip assigned", "Assigning ALL IP including background IP is extremely broad"),
        ("worldwide non-compete", "Non-compete with no geographic limit is likely unenforceable but chilling"),
    ]
    MEDIUM_RISK_PATTERNS = [
        ("non-compete", "Non-compete clauses restrict future employment; check duration and geography"),
        ("non-solicitation", "Restricts your ability to work with certain people/clients after contract"),
        ("broad ip", "IP assignment may cover more than work product; clarify scope"),
        ("short notice", "Short notice period limits your ability to plan transitions"),
        ("no arbitration", "Litigation can be slow and expensive; arbitration is often preferable"),
        ("no dispute resolution", "No mechanism for resolving disputes is a gap in the contract"),
        ("automatic termination", "Automatic termination on certain events may catch you off-guard"),
        ("3-year non-compete", "3-year non-compete duration is likely excessive and may be unenforceable"),
        ("no payment on termination", "Should receive payment for work completed prior to termination"),
        ("consequential damages", "Exposure to consequential/indirect damages can be enormous"),
    ]
    LOW_RISK_PATTERNS = [
        ("30-day notice", "30-day notice period is standard and reasonable"),
        ("mutual nda", "Mutual NDA is balanced - both parties protected equally"),
        ("governing law", "Governing law is specified - good practice"),
        ("force majeure", "Force majeure clause present - protects against unforeseeable events"),
        ("arbitration", "Arbitration clause present - faster and cheaper dispute resolution"),
        ("liability cap", "Liability is capped - limits financial exposure"),
        ("cure period", "Cure period present - gives opportunity to remedy breaches"),
        ("severability", "Severability clause means one bad provision won't void the whole contract"),
    ]

    clauses = [c.strip().lower() for c in clauses_list.replace('\n', ',').split(',') if c.strip()]
    
    results = []
    high_count = 0
    medium_count = 0
    low_count = 0

    for clause in clauses:
        matched = False
        for pattern, explanation in HIGH_RISK_PATTERNS:
            if pattern in clause:
                results.append(f"🔴 HIGH RISK   | {clause.title()}\n              → {explanation}")
                high_count += 1
                matched = True
                break
        if not matched:
            for pattern, explanation in MEDIUM_RISK_PATTERNS:
                if pattern in clause:
                    results.append(f"🟡 MEDIUM RISK | {clause.title()}\n              → {explanation}")
                    medium_count += 1
                    matched = True
                    break
        if not matched:
            for pattern, explanation in LOW_RISK_PATTERNS:
                if pattern in clause:
                    results.append(f"🟢 LOW RISK    | {clause.title()}\n              → {explanation}")
                    low_count += 1
                    matched = True
                    break
        if not matched:
            results.append(f"⚪ UNCLASSIFIED | {clause.title()}\n              → Requires manual legal review")

    # Overall score (0-10, 10 = highest risk)
    total = len(clauses) if clauses else 1
    raw_score = (high_count * 3 + medium_count * 1.5) / total
    overall_score = min(10, round(raw_score * 2.5, 1))

    verdict = (
        "🔴 HIGH RISK CONTRACT — Seek legal advice before signing" if overall_score >= 7 else
        "🟡 MODERATE RISK — Several clauses need negotiation" if overall_score >= 4 else
        "🟢 MANAGEABLE RISK — Minor issues, review before signing"
    )

    output = "\n━━━ CLAUSE RISK ASSESSMENT ━━━\n\n"
    output += "\n\n".join(results)
    output += f"""

━━━ RISK SUMMARY ━━━

🔴 High Risk Clauses:    {high_count}
🟡 Medium Risk Clauses:  {medium_count}
🟢 Low Risk / Good:      {low_count}
⚪ Unclassified:         {len(clauses) - high_count - medium_count - low_count}

📊 Overall Risk Score:   {overall_score} / 10
⚖️  Verdict:             {verdict}
"""
    return output

# TOOL 3: Legal Math 
def legal_math(
    operation: str,
    values: str,
    description: str = ""
) -> str:
    """
    Perform safe arithmetic calculations relevant to contracts.
    Useful for calculating penalties, prorated payments, interest, total contract value.

    Args:
        operation: One of 'sum', 'multiply', 'percentage', 'prorate', 'compound_interest', 'penalty'.
        values: Comma-separated numeric values needed for the operation.
                For 'prorate': 'total_value,days_completed,total_days'
                For 'compound_interest': 'principal,annual_rate_percent,years'
                For 'penalty': 'contract_value,penalty_percent'
                For 'percentage': 'value,percent'
                For 'sum' or 'multiply': list of numbers
        description: Optional description of what is being calculated (for context in output).

    Returns:
        Calculated result with explanation.
    """
    try:
        nums = [float(x.strip()) for x in values.split(',')]
    except ValueError:
        return "Error: Could not parse values. Please provide comma-separated numbers."

    label = f" ({description})" if description else ""

    try:
        if operation == "sum":
            result = sum(nums)
            breakdown = " + ".join(f"{n:,.2f}" for n in nums)
            return f"Sum{label}:\n{breakdown} = {result:,.2f}"

        elif operation == "multiply":
            result = 1
            for n in nums: result *= n
            breakdown = " × ".join(f"{n:,.2f}" for n in nums)
            return f"Product{label}:\n{breakdown} = {result:,.2f}"

        elif operation == "percentage":
            if len(nums) < 2:
                return "Error: 'percentage' requires 2 values: value, percent"
            value, percent = nums[0], nums[1]
            result = value * (percent / 100)
            return f"Percentage{label}:\n{percent}% of {value:,.2f} = {result:,.2f}"

        elif operation == "prorate":
            if len(nums) < 3:
                return "Error: 'prorate' requires 3 values: total_value, days_completed, total_days"
            total, completed, total_days = nums[0], nums[1], nums[2]
            result = (completed / total_days) * total
            remaining = total - result
            return (f"Prorated Payment{label}:\n"
                    f"Total Contract Value: {total:,.2f}\n"
                    f"Days Completed: {completed:.0f} of {total_days:.0f}\n"
                    f"Amount Earned: {result:,.2f}\n"
                    f"Amount Remaining: {remaining:,.2f}")

        elif operation == "compound_interest":
            if len(nums) < 3:
                return "Error: 'compound_interest' requires 3 values: principal, annual_rate_percent, years"
            principal, rate, years = nums[0], nums[1]/100, nums[2]
            final = principal * (1 + rate) ** years
            interest = final - principal
            return (f"Compound Interest{label}:\n"
                    f"Principal:    {principal:,.2f}\n"
                    f"Annual Rate:  {nums[1]}%\n"
                    f"Period:       {years:.0f} years\n"
                    f"Final Amount: {final:,.2f}\n"
                    f"Interest:     {interest:,.2f}")

        elif operation == "penalty":
            if len(nums) < 2:
                return "Error: 'penalty' requires 2 values: contract_value, penalty_percent"
            contract_val, penalty_pct = nums[0], nums[1]
            penalty = contract_val * (penalty_pct / 100)
            return (f"Penalty Calculation{label}:\n"
                    f"Contract Value:   {contract_val:,.2f}\n"
                    f"Penalty Rate:     {penalty_pct}%\n"
                    f"Penalty Amount:   {penalty:,.2f}\n"
                    f"Net After Penalty: {contract_val - penalty:,.2f}")

        else:
            return f"Error: Unknown operation '{operation}'. Use: sum, multiply, percentage, prorate, compound_interest, penalty"

    except Exception as e:
        return f"Calculation error: {str(e)}"