-- Pieces are identified by (data_set_id, piece_id); duplicates mean a bad join or replayed event.
select data_set_id, piece_id, count(*) as n
from model.pdp_pieces
group by 1, 2
having count(*) > 1
