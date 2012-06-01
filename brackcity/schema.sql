drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name string not null,
  username string not null,
  pw_hash string not null
);
