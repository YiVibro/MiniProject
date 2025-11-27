-- SECURITY DEFINER RPCs to expose leaderboard safely without loosening table RLS

-- All-time and weekly leaderboard via views, enriched with public profile info
CREATE OR REPLACE FUNCTION public.get_leaderboard(
  p_scope text,
  p_limit integer DEFAULT 100,
  p_offset integer DEFAULT 0
)
RETURNS TABLE (
  user_id uuid,
  rank integer,
  total_xp bigint,
  weekly_xp bigint,
  name text,
  avatar_url text
) AS $$
BEGIN
  IF lower(COALESCE(p_scope, 'weekly')) = 'weekly' THEN
    RETURN QUERY
      SELECT lw.user_id,
             lw.rank,
             NULL::bigint AS total_xp,
             COALESCE(lw.weekly_xp, 0) AS weekly_xp,
             up.name,
             up.avatar_url
      FROM leaderboard_weekly lw
      LEFT JOIN user_profiles up ON up.user_id = lw.user_id
      ORDER BY lw.rank
      OFFSET GREATEST(p_offset, 0)
      LIMIT GREATEST(p_limit, 0);
  ELSE
    RETURN QUERY
      SELECT la.user_id,
             la.rank,
             COALESCE(la.total_xp, 0) AS total_xp,
             NULL::bigint AS weekly_xp,
             up.name,
             up.avatar_url
      FROM leaderboard_all_time la
      LEFT JOIN user_profiles up ON up.user_id = la.user_id
      ORDER BY la.rank
      OFFSET GREATEST(p_offset, 0)
      LIMIT GREATEST(p_limit, 0);
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Per-user rank in a given scope
CREATE OR REPLACE FUNCTION public.get_user_rank(
  p_user uuid,
  p_scope text
)
RETURNS TABLE (
  user_id uuid,
  rank integer,
  total_xp bigint,
  weekly_xp bigint
) AS $$
BEGIN
  IF lower(COALESCE(p_scope, 'weekly')) = 'weekly' THEN
    RETURN QUERY
      SELECT lw.user_id, lw.rank, NULL::bigint AS total_xp, COALESCE(lw.weekly_xp,0) AS weekly_xp
      FROM leaderboard_weekly lw
      WHERE lw.user_id = p_user
      LIMIT 1;
  ELSE
    RETURN QUERY
      SELECT la.user_id, la.rank, COALESCE(la.total_xp,0) AS total_xp, NULL::bigint AS weekly_xp
      FROM leaderboard_all_time la
      WHERE la.user_id = p_user
      LIMIT 1;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Restrict execution to authenticated role (do not grant to anon unless desired)
REVOKE ALL ON FUNCTION public.get_leaderboard(text, integer, integer) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.get_user_rank(uuid, text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.get_leaderboard(text, integer, integer) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_rank(uuid, text) TO authenticated;
