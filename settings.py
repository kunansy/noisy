from environs import Env

env = Env()
env.read_env()

MAX_DEPTH = env.int("MAX_DEPTH", 25)
MIN_SLEEP = env.int("MIN_SLEEP", 3)
MAX_SLEEP = env.int("MAX_SLEEP", 6)
TIMEOUT = env.int("TIMEOUT")

ROOT_URLS = env.list("ROOT_URLS")
BLACKLISTED_URLS = env.list("blacklisted_urls")
USER_AGENTS = env.list("USER_AGENTS")

LOG_LEVEL = env.log_level("LOG_LEVEL")
