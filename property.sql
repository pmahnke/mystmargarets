CREATE TABLE info (
last_update date
);

CREATE TABLE property (
id integer primary key autoincrement,
agent text,
agent_logo text,
agent_url text,
agent_email text,
title text,
decr text,
image text,
url text,
price text, 
type text,
date date
);

insert into info (last_update) values (date('now', '-1 day'));
update info set last_update = (date('now', '-1 day'));
