select
    *
from filecoin_daily_metrics
where date < (select max(date) from filecoin_daily_metrics) - interval '1 day'
