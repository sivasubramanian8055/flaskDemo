-- -- PostgreSQL database dump -- 
-- Dumped from database version 11.2 (Debian 11.2-1.pgdg90+1) 
-- Dumped by pg_dump version 11.3 
-- Started on 2019-08-06 00:17:49 CDT 
SET statement_timeout = 0; 
SET lock_timeout = 0; 
SET idle_in_transaction_session_timeout = 0; 
SET client_encoding = 'UTF8'; 
SET standard_conforming_strings = on; 
SELECT pg_catalog.set_config('search_path', '', false); 
SET check_function_bodies = false; 
SET xmloption = content; 
SET client_min_messages = warning; 
SET row_security = off; 
SET default_tablespace = ''; 
SET default_with_oids = false; 

CREATE TYPE Public.ACCOUNT_TYPE AS ENUM ('Admin','Savings Account', 'Salary Account', 'Current Account');

CREATE TYPE Public.TRANSACTION_TYPE AS ENUM ('Debit', 'Credit');

CREATE TABLE IF NOT EXISTS public.users
( id SERIAL UNIQUE NOT NULL, name varchar(250) NOT NULL, account_type Public.ACCOUNT_TYPE NOT NULL,password varchar(8) NOT NULL, balance INT NOT NULL, street varchar(250) NOT NULL, city varchar(250) NOT NULL, state varchar(250) NOT NULL, zip varchar(250) NOT NULL, ph_no varchar(250) NOT NULL, dob date NOT NULL,is_account_active boolean NOT NULL, PRIMARY KEY (id) );

CREATE TABLE IF NOT EXISTS public.transactions 
( id INT GENERATED ALWAYS AS IDENTITY NOT NULL, user_id INT NOT NULL, trans_type Public.TRANSACTION_TYPE , trans_amount INT NOT NULL, beneficiary INT DEFAULT 0 , withdraw_time DATE NOT NULL, PRIMARY KEY (id), FOREIGN KEY(user_id) REFERENCES Public.users(id) );

ALTER SEQUENCE Public.users_id_seq RESTART WITH 2;

insert into Public.users values (1,'admin','Admin','admin',0,'street','city','state',0,0,'2022-10-20','true') ON CONFLICT DO NOTHING;