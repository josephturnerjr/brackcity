drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name TEXT not null,
  username TEXT not null,
  pw_hash TEXT not null
);
create index user_index on users (username);

drop table if exists admins;
create table admins (
  id integer primary key autoincrement,
  user_id integer not null
);
create index admin_user_id_index on admins (user_id);

drop table if exists sessions;
create table sessions(
  id integer primary key autoincrement,
  user_id integer not null,
  session_id TEXT not null,
  creation_date TEXT not null,
  is_admin BOOLEAN not null
);
create index session_id_index on sessions (session_id);

drop table if exists contests;
create table contests (
  id integer primary key autoincrement,
  user_id integer not null,
  name TEXT not null,
  type TEXT not null
);
drop table if exists players;
create table players(
  id integer primary key autoincrement,
  contest_id integer not null,
  name TEXT not null,
  user_id integer
);
drop table if exists games;
create table games(
  id integer primary key autoincrement,
  date TEXT not null,
  contest_id integer
);
drop table if exists scores;
create table scores(
  id integer primary key autoincrement,
  game_id integer not NULL,
  player_id integer not NULL,
  score REAL not null
);

