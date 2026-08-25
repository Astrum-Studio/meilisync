# MongoDB

meilisync uses [change streams](https://www.mongodb.com/docs/manual/changeStreams/) via [motor](https://motor.readthedocs.io/). A **replica set** is required (even a single-node set).

## Install extra

```bash
pip install "meilisync[mongodb]"
```

## Config

```yaml
source:
  type: mongo
  host: 127.0.0.1
  port: 27017
  username: root
  password: secret
  database: app
  replicaSet: rs0
```

Extra keys are passed to `AsyncIOMotorClient`.

`sync[].table` is the **collection** name. Use `pk: _id` unless you map another identifier. Document `_id` values are stored as strings in Meilisearch.

Progress stores a `resume_token` so the stream can continue after a restart.
