select min(date) as first_date, max(date) as last_date, count(*) as days
from model.network_daily_fevm_checkpoints
where date < current_date
having date_diff('day', min(date), max(date)) + 1 != count(*)
