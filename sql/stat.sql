SELECT
  S.name,
  S.tier,
  count(*)
FROM Battle b
  JOIN Ships S ON b.player_ship_id = S.ship_id
WHERE b.date > date('now', 'start of month', '-1 month')
      AND b.type = 'pvp'
GROUP BY b.player_ship_id
ORDER BY 2 DESC;
SELECT
  S.tier,
  count(*)
FROM Battle b
  JOIN Ships S ON b.player_ship_id = S.ship_id
WHERE b.date > date('now', 'start of month', '-1 month')
      AND b.type = 'pvp'
GROUP BY S.tier
ORDER BY 1 DESC;
SELECT
  Member.battle_id,
  count(S2.name)
FROM Battle b
  JOIN Ships S ON b.player_ship_id = S.ship_id
  JOIN BattleMembers Member ON b.battle_id = Member.battle_id AND Member.relation = 2
  JOIN Ships S2 ON Member.ship_id = S2.ship_id
WHERE b.date > date('now', 'start of month', '-1 month')
      AND b.type = 'pvp'
      AND S.tier = 8
GROUP BY Member.battle_id;
SELECT count()
FROM Players;
SELECT
  p.nickname,
  count(*)
FROM BattleMembers b
  JOIN Players p ON b.player_id = p.player_id
GROUP BY b.player_id
HAVING count(*)> 5
ORDER BY 2 desc;
--
SELECT P.nickname, S.name
FROM Battle b
JOIN BattleMembers Member ON b.battle_id = Member.battle_id
JOIN Ships S ON Member.ship_id = S.ship_id
  JOIN Players P ON Member.player_id = P.player_id
WHERE Member.relation IN (1, 0) AND 
  b.battle_id = 3210
