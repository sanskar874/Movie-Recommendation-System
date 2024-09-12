from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
import urllib.request, json
import pickle
import requests
import numpy as np
import pandas as pd


#movie_pivot = pickle.load(open('movie_pivot.pkl','rb'))
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))


app=Flask(__name__)
app.secret_key=os.urandom(24)

conn=mysql.connector.connect(host='localhost', user='root', password='123456', database='movie_recommendation')
cursor=conn.cursor()




@app.route('/')
def login():
    return render_template('login.html')




@app.route('/register')
def register():
    return render_template('register.html')




@app.route('/home')
def home():
    if 'userid' in session:
        index = movies[movies['title'] == 'Thor'].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []
        for i in distances[1:17]:
            movie_id = movies[movies['title'] == movies.iloc[i[0]].title]['movie_id'].values
            if movie_id.size!=0:
                movie_id=movie_id[0]
            else: 
                movie_id = 285
    
        
            url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
            data = requests.get(url)
            json_data = data.json()
            poster_path = json_data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            recommended_movie_posters.append(full_path)
            recommended_movie_names.append(movies.iloc[i[0]].title)
        
        return render_template('home.html', titles=recommended_movie_names, poster=recommended_movie_posters)
    
    
        #  return render_template('index.html',
        #                    movie_names= list(popular_movies['title'].values),
        #                    director=list(popular_movies['author'].values),
        #                    votes=list(popular_movies['num_ratings'].values),
        #                    ratings=list(popular_movies['avg_ratings'].values),
        #                    images=list(popular_movies['image'].values))
    else: 
        return redirect('/')



@app.route('/login_validation', methods=['POST'])
def login_validation():
    userid=request.form.get('userid')
    password=request.form.get('password')
    
    cursor.execute("select * from users where userid='{}' and password='{}';".format(userid, password))
    users=cursor.fetchall()
    if len(users)==1:
        session['userid']=users[0][0]
        return redirect('/home')
    else:
        return redirect('/')
    


    
@app.route('/add_user', methods=['POST'])
def add_user():
    userid=request.form.get('new_userid')
    password=request.form.get('new_password')
    cursor.execute("select * from users where userid='{}';".format(userid))
    validate_user=cursor.fetchall()
    if len(validate_user)>0:
        return redirect('/')
    else:
        cursor.execute("insert into users values('{}', '{}');".format(userid, password))
        conn.commit()

        cursor.execute("select * from users where userid='{}' and password='{}';".format(userid, password))
        new_user=cursor.fetchall()
        session['userid']=new_user[0][0]
        return redirect('/home')




@app.route('/logout')
def logout():
    session.pop('userid')
    return redirect('/')



@app.route('/about_us')
def about_us():
    if 'userid' in session:
        return render_template('about_us.html')
    else:
        return redirect('/')



@app.route('/recommend')
def recommend_ui():
    if 'userid' in session:
        return render_template('recommend.html')
    else:
        return redirect('/')




@app.route('/recommend_movies', methods=["post"])
def recommend():
    user_input= request.form.get("user_input")
    index = movies[movies['title'] == user_input].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:17]:
        # fetch the movie poster
        # movie_id = 285
        
        # for tempmovie_id, movie_info, temptags in movies.items():
        #     if movie_info == user_input:
        #         movie_id = tempmovie_id
        #         break
        
        
        # for tempmovie_id, temptitle, tempgenre in movies:
        #     if temptitle == user_input:
        #         movie_id = tempmovie_id 
        #         break
        
        # np.where(movie_pivot.index == user_input)[0][2]
        movie_id = movies[movies['title'] == movies.iloc[i[0]].title]['movie_id'].values
        if movie_id.size!=0:
            movie_id=movie_id[0]
        else: 
            movie_id = 285
    
        
        url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
        data = requests.get(url)
        json_data = data.json()
        poster_path = json_data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        recommended_movie_posters.append(full_path)
        recommended_movie_names.append(movies.iloc[i[0]].title)
        
    return render_template('recommend.html', titles=recommended_movie_names, poster=recommended_movie_posters)
    





if __name__=="__main__":
    app.run(debug=True)
