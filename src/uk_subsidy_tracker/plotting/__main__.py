from uk_subsidy_tracker.plotting.cannibalisation.capture_ratio import main as capture_ratio
from uk_subsidy_tracker.plotting.cannibalisation.price_vs_wind import main as price_vs_wind
from uk_subsidy_tracker.plotting.capacity_factor.monthly import main as cf_monthly
from uk_subsidy_tracker.plotting.capacity_factor.seasonal import main as cf_seasonal
from uk_subsidy_tracker.plotting.intermittency.generation_heatmap import main as heatmap
from uk_subsidy_tracker.plotting.intermittency.load_duration import main as load_duration
from uk_subsidy_tracker.plotting.intermittency.rolling_minimum import main as rolling_minimum
from uk_subsidy_tracker.plotting.subsidy.bang_for_buck import main as bang_for_buck
from uk_subsidy_tracker.plotting.subsidy.lorenz import main as lorenz
from uk_subsidy_tracker.plotting.subsidy.cfd_dynamics import main as cfd_dynamics
from uk_subsidy_tracker.plotting.subsidy.cfd_vs_gas_cost import main as cfd_vs_gas_total
from uk_subsidy_tracker.plotting.subsidy.cfd_payments_by_category import (
    main as cfd_payments_by_category,
)
from uk_subsidy_tracker.plotting.subsidy.remaining_obligations import (
    main as remaining_obligations,
)
from uk_subsidy_tracker.plotting.subsidy.scissors import main as scissors
from uk_subsidy_tracker.plotting.subsidy.subsidy_per_avoided_co2_tonne import (
    main as subsidy_per_avoided_co2_tonne,
)

# Subsidy economics
cfd_vs_gas_total()
cfd_dynamics()
cfd_payments_by_category()
scissors()
subsidy_per_avoided_co2_tonne()
bang_for_buck()
remaining_obligations()
lorenz()

# Capacity factor
cf_monthly()
cf_seasonal()

# Intermittency
heatmap()
load_duration()
rolling_minimum()

# Cannibalisation
capture_ratio()
price_vs_wind()
