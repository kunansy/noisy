from environs import Env

env = Env()
env.read_env()

LOG_FMT = "{levelname:<7} [{asctime},{msecs:3.0f}] " \
          "[{funcName}():{lineno}] {message}"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

REQUEST_TIMEOUT = env.int("REQUEST_TIMEOUT", 5)
MAX_DEPTH = env.int("MAX_DEPTH", 25)
MIN_SLEEP = env.int("MIN_SLEEP", 3)
MAX_SLEEP = env.int("MAX_SLEEP", 6)
TIMEOUT = env.int("TIMEOUT")

ROOT_URLS = env.list("ROOT_URLS")
BLACKLISTED_URLS = env.list("blacklisted_urls")
USER_AGENTS = env.list("USER_AGENTS")

LOG_LEVEL = env.log_level("LOG_LEVEL")
