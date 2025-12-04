create database IMDb_TOP250_database;
use IMDb_TOP250_database;

create table imdb_movies(
movie_id varchar(100) primary key,
movie_name varchar(255) not null,
movie_imgpath varchar(255),
movie_length_min int,
movie_path varchar(255));


create table genres (
genres_number int  primary key auto_increment,
genre_name varchar(100) NOT null
);

create table genres_movie (
genres_number int ,
movie_id varchar(100),

primary key(genres_number,movie_id),
Foreign key (genres_number) references genres(genres_number),
Foreign key (movie_id) references imdb_movies(movie_id));

create table roles (
role_number int auto_increment primary key,
role_name varchar(255),
role varchar(150),
UNIQUE KEY  (role_name, role)
);

create table roles_movie (
role_number int ,
movie_id varchar(100),

primary key(role_number,movie_id),
Foreign key (role_number) references roles(role_number),
Foreign key (movie_id) references imdb_movies(movie_id));


create table country (
country_number int primary key auto_increment ,
country varchar(150) 
);


create table country_movie (
country_number int ,
movie_id varchar(100),

primary key(country_number,movie_id),
Foreign key (country_number) references country(country_number),
Foreign key (movie_id) references imdb_movies(movie_id));

create table level (
level_number int primary key auto_increment ,
level varchar(100) 
);

create table level_movie (
level_number int ,
movie_id varchar(100),

primary key(level_number,movie_id),
Foreign key (level_number) references level(level_number),
Foreign key (movie_id) references imdb_movies(movie_id));


create table scrapetime_rating(
scrapetime_number int auto_increment primary key,
movie_id varchar(100),
scrape_date date,
rating int,

foreign key (movie_id) references imdb_movies(movie_id)
);

show warnings;


show warnings;

SHOW TABLES;

ALTER TABLE IMDb_movies
ADD COLUMN storyline TEXT;

ALTER TABLE imdb_movies
ADD COLUMN year int;

ALTER TABLE scrapetime_rating
MODIFY COLUMN rating DECIMAL(3,1);


