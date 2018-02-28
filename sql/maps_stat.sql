SELECT

  maps.name,
  maps.icon,
  count()
FROM Battle battle
  JOIN maps maps ON maps.map_id = battle.map_id
  JOIN Ships S ON battle.player_ship_id = S.ship_id
WHERE battle.date > date('now', 'start of month', '-1 month')
GROUP BY  battle.map_id