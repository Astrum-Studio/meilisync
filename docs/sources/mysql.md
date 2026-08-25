# MySQL

meilisync reads the binary log in `ROW` format through [asyncmy](https://github.com/long2ice/asyncmy).

## Server settings

```ini
binlog_format = ROW
binlog_row_image = FULL
```

The user needs `REPLICATION SLAVE`, `REPLICATION CLIENT`, and `SELECT` on the synced tables.

```sql
CREATE USER 'meilisync'@'%' IDENTIFIED BY 'secret';
GRANT SELECT, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'meilisync'@'%';
FLUSH PRIVILEGES;
```

## Install extra

```bash
pip install "meilisync[mysql]"
```

## Config

```yaml
source:
  type: mysql
  host: 127.0.0.1
  port: 3306
  user: meilisync
  password: secret
  database: app
  server_id: 1
```

`server_id` identifies this binlog client. Default `1`. It must be unique among replicas / CDC consumers on that server.

Progress stores the binlog file name and position so a restart continues from the last event.
