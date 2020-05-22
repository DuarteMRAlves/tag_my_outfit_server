import pstats

STATS_FILE = '/logs/profile.pstats'
stats = pstats.Stats(STATS_FILE)
stats.strip_dirs()
stats.sort_stats('cumtime')

stats.print_stats(0.3)
