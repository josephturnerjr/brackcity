drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name TEXT unique not null,
  username TEXT not null,
  pw_hash TEXT not null
);
