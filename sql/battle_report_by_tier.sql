-- Статистика сыграных боев по уровню с опеределеной даты
WITH battle_report AS (
    SELECT
      s_b.tier AS player_tier,
      bm.battle_id,
      S.tier   AS enemy_tier,
      count()
    FROM BattleMembers bm
      JOIN Ships S ON bm.ship_id = S.ship_id
      JOIN Battle B ON bm.battle_id = B.battle_id
      JOIN Ships s_b ON B.player_ship_id = s_b.ship_id
    WHERE B.date > date('now', 'start of month', '-1 month')
          AND B.type = 'pvp'
          AND bm.relation = 2
    GROUP BY s_b.tier, bm.battle_id, S.tier),
    max_ship_tier_report AS (
      SELECT
        br.player_tier     AS player_tier,
        max(br.enemy_tier) AS max_enemy_tier
      FROM battle_report br
      GROUP BY br.player_tier, br.battle_id),
    battle_count_by_tier AS (
      SELECT
        player_tier AS player_tier,
        count()     AS count_battle
      FROM max_ship_tier_report
      GROUP BY player_tier)
SELECT
  max_rep.player_tier                      AS player_tier,
  max_rep.max_enemy_tier                   AS max_enemy_tier,
  count()                                  AS count_battle,
  round(100.0 * count() / count_battle, 2) AS percent,
  count_battle_on_tier.count_battle        AS count_all_battle_by_tier
FROM max_ship_tier_report max_rep
  JOIN
  (SELECT *
   FROM battle_count_by_tier) AS count_battle_on_tier
    ON count_battle_on_tier.player_tier = max_rep.player_tier
GROUP BY max_rep.player_tier, max_rep.max_enemy_tier;
-- Статистика сыграных боев по уровню, группировка по месяцам
WITH battle_report AS (
    SELECT
      strftime('%Y-%m', B.date) AS month,
      s_b.tier                  AS player_tier,
      bm.battle_id,
      S.tier                    AS enemy_tier,
      count()
    FROM BattleMembers bm
      JOIN Ships S ON bm.ship_id = S.ship_id
      JOIN Battle B ON bm.battle_id = B.battle_id
      JOIN Ships s_b ON B.player_ship_id = s_b.ship_id
    WHERE B.type = 'pvp'
          AND bm.relation = 2
    GROUP BY strftime('%Y-%m', B.date), s_b.tier, bm.battle_id, S.tier),
    max_ship_tier_report AS (
      SELECT
        br.month           AS month,
        br.player_tier     AS player_tier,
        max(br.enemy_tier) AS max_enemy_tier
      FROM battle_report br
      GROUP BY br.month, br.player_tier, br.battle_id),
    battle_count_by_tier AS (
      SELECT
        month,
        player_tier AS player_tier,
        count()     AS count_battle
      FROM max_ship_tier_report
      GROUP BY month, player_tier)
SELECT
  max_rep.month,
  max_rep.player_tier                                    AS player_tier,
  max_rep.max_enemy_tier                                 AS max_enemy_tier,
  count()                                                AS count_battle,
  round(100.0 * count() / sum(DISTINCT count_battle), 2) AS percent,
  sum(count_battle_on_tier.count_battle)                 AS count_all_battle_by_tier
FROM max_ship_tier_report max_rep
  JOIN
  (SELECT *
   FROM battle_count_by_tier) AS count_battle_on_tier
    ON count_battle_on_tier.player_tier = max_rep.player_tier AND count_battle_on_tier.month = max_rep.month
WHERE max_rep.month > '2017-10' AND max_rep.player_tier = 8
GROUP BY max_rep.month, max_rep.player_tier, max_rep.max_enemy_tier;
-- Статистика сыграных боев по кораблью
WITH battle_report AS (
    SELECT
      strftime('%Y-%m', B.date) AS month,
      s_b.ship_id,
      bm.battle_id,
      S.tier                    AS enemy_tier,
      count()
    FROM BattleMembers bm
      JOIN Ships S ON bm.ship_id = S.ship_id
      JOIN Battle B ON bm.battle_id = B.battle_id
      JOIN Ships s_b ON B.player_ship_id = s_b.ship_id
    WHERE B.type = 'pvp'
          AND bm.relation = 2
    GROUP BY strftime('%Y-%m', B.date), s_b.name, s_b.tier, bm.battle_id, S.tier),
    max_ship_tier_report AS (
      SELECT
        br.month           AS month,
        br.ship_id,
        max(br.enemy_tier) AS max_enemy_tier
      FROM battle_report br
      GROUP BY br.month, br.ship_id, br.battle_id),
    battle_count_by_ship AS (
      SELECT
        month,
        ship_id,
        count() AS count_battle
      FROM max_ship_tier_report
      GROUP BY month, ship_id)
SELECT
  max_rep.month,
  ship.name,
  max_rep.max_enemy_tier                                 AS max_enemy_tier,
  count()                                                AS count_battle,
  round(100.0 * count() / sum(DISTINCT count_battle), 2) AS percent,
  sum(DISTINCT count_battle_on_tier.count_battle)        AS count_all_battle_by_tier
FROM max_ship_tier_report max_rep
  JOIN
  (SELECT *
   FROM battle_count_by_ship) AS count_battle_on_tier
    ON count_battle_on_tier.month = max_rep.month AND count_battle_on_tier.ship_id = max_rep.ship_id
  JOIN Ships ship ON max_rep.ship_id = ship.ship_id
WHERE max_rep.month > '2017-10' AND ship.name = 'Normandie'
GROUP BY max_rep.month, max_rep.ship_id, max_rep.max_enemy_tier
ORDER BY max_rep.month, max_rep.max_enemy_tier;

