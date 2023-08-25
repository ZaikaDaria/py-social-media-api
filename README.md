# Social-Media-Api

Social media API service for managing with DRF.
You can manage  with users, posts, comments, likes, follows.

# Installing
You can use this commands to install project on you own localhost.

* Python 3 should be installed. Docker should be installed.
```shell
git clone https://github.com/ZaikaDaria/py-social-media-api.git
cd social_media
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
* Create .env file in base directory
* Fill .env file with data
```
SECRET_KEY=SECRET_KEY
```
* Make migrations
* Use "python manage.py runserver" to start

# To use authenticate system

* /api/user/register - to create user
* /api/user/token - to get token

# Features
1. JSON Web Token authenticated  
2. Documentation /api/doc/swagger/
3. Creating users, posts
4. Managing user's profile and retrieve profiles of other users
5. Filtering users by email and username
6. Users can follow and unfollow to each others
7. Users can like and dislike posts
8. Users can comment different posts
9. Implemented different permissions for different actions.
