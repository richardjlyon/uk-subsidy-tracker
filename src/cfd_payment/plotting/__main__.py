from cfd_payment.plotting.cumulative_payments import main as cumulative_payments
from cfd_payment.plotting.cumulative_payments_by_company import (
    main as cumulative_payments_by_company,
)
from cfd_payment.plotting.cfd_vs_gas_cost import main as cfd_vs_gas_cost
from cfd_payment.plotting.payments_vs_gas_price import main as payments_vs_gas_price
from cfd_payment.plotting.subsidy_per_avoided_co2_tonne import (
    main as subsidy_per_avoided_co2_tonne,
)

cumulative_payments()
cumulative_payments_by_company()
cfd_vs_gas_cost()
payments_vs_gas_price()
subsidy_per_avoided_co2_tonne()
