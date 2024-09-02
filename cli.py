
import sentry_sdk

sentry_sdk.init(
    dsn="https://7ca766726f13e2fedaf654f7d4401130@o4507843819405312.ingest.de.sentry.io/4507843832053840",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)