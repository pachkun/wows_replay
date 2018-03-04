SELECT
  bm.player_id,
  count()
FROM BattleMembers bm
WHERE bm.relation = 1
GROUP BY bm.player_id
HAVING count() > (SELECT count()
                  FROM Battle) / 100;
SELECT
  b.battle_id,
  count(Member.player_id),
  max(S.tier)
FROM Battle b
  JOIN BattleMembers Member ON b.battle_id = Member.battle_id
  JOIN Ships S ON Member.ship_id = S.ship_id
WHERE Member.relation IN (1, 0)
      AND b.type = 'pvp'
      AND Member.player_id IN (1,
                               12,
                               265,
                               482)
      AND b.date > date('now', 'start of day', '-30 day')
GROUP BY b.battle_id;