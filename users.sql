-- Adminer 6.1.0 PostgreSQL 18.3 dump

DROP TABLE IF EXISTS "public"."users";

CREATE TABLE "public"."users" (
    "id" character varying(15) NOT NULL,
    "pwd" character varying(30) NOT NULL,
    "nickname" character varying(30) NOT NULL
);

INSERT INTO "public"."users" ("id", "pwd", "nickname") VALUES
('john',	'123',	'約翰'),
('mary',	'123',	'馬麗');

-- 2026-10-16 10:11:14 UTC
