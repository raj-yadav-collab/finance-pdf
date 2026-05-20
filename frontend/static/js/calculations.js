/* Calculation engine for live preview */

const PRIVATE_RESERVE_MULTIPLIER = 6;

function calculateSACS(inflow, outflow, insurance_deductibles, privateReserveBalance, schwabBalance) {
    const excess = inflow - outflow;
    const privateReserveTarget = (PRIVATE_RESERVE_MULTIPLIER * outflow) + insurance_deductibles;
    
    return {
        inflow: inflow,
        outflow: outflow,
        excess: excess,
        private_reserve_balance: privateReserveBalance,
        private_reserve_target: privateReserveTarget,
        schwab_investment_balance: schwabBalance
    };
}

function calculateTCC(accounts, balances) {
    let client1RetirementTotal = 0;
    let client2RetirementTotal = 0;
    let nonRetirementTotal = 0;
    let trustTotal = 0;
    let liabilitiesTotal = 0;
    
    accounts.forEach(account => {
        const balance = balances[account.id] || 0;
        
        if (account.account_type === 'retirement_1') {
            client1RetirementTotal += balance;
        } else if (account.account_type === 'retirement_2') {
            client2RetirementTotal += balance;
        } else if (account.account_type === 'non_retirement') {
            nonRetirementTotal += balance;
        } else if (account.account_type === 'trust') {
            trustTotal += balance;
        } else if (account.account_type === 'liability') {
            liabilitiesTotal += balance;
        }
    });
    
    const grandTotal = client1RetirementTotal + client2RetirementTotal + nonRetirementTotal + trustTotal;
    
    return {
        client_1_retirement_total: client1RetirementTotal,
        client_2_retirement_total: client2RetirementTotal > 0 ? client2RetirementTotal : null,
        non_retirement_total: nonRetirementTotal,
        trust_total: trustTotal,
        grand_total: grandTotal,
        liabilities_total: liabilitiesTotal,
        account_balances: balances
    };
}
