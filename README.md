# CSE106 Final Project

## Group Members
- Jamie Mariz Laudencia
- Hao Mai
- Tony Doan
- Jennifer Nhu

## Description and Features
Project: Social Media Web Application (using python (Flask)) hosted live 

- User will sign up and login to account (with hashed/salted passwords) 
- User will be able to create new post with some description and an image
- User will be able to write his status 
- User will be able to see all the statuses and posts of other users 
- User will be able to like posts of others 
- User will be able to share posts of his and others to anyone 
- User will be able follow or unfollow other users 
- Conclusion: User will be able to access information about themselves or others from the database through the server from the front end

## Requirements
- flask
- flask-sqlalchemy
- flask-login
- flask-bcrypt

## Creating a new database
Run the following commands to create new table

* set FLASK\_APP=views 
* flask shell
Shell will be opened
* from models import db,Post,User,Like,Share,Follow
* db.create\_all()
