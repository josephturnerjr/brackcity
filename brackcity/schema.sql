drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name TEXT not null,
  username TEXT not null,
  pw_hash TEXT not null
);
drop table if exists contests;
create table contests (
  id integer primary key autoincrement,
  user_id integer not null,
  name TEXT not null
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
