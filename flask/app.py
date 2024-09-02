import nltk
# nltk.download('punkt')

from flask import Flask, request, render_template, session
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from nltk.stem.snowball import SnowballStemmer
from user_functions import stem_and_vectorize_products_based_on_metadata, generate_recs, get_sample_product, recommend_diverse_products
import pandas as pd
import numpy as np
import pickle

port_no = 4000
# template_dir = 'templates'
# static_dir = 'static'
app = Flask(__name__) #, template_folder=template_dir, static_folder=static_dir)
# ngrok.set_auth_token("23H0IY10fqeKMIW7kG05JhKZMae_3Zabr2iqkU9AUcZ7CrRTP") 
# ngrok.set_auth_token("2BWuK5kiY9aU6289pnRKPsAYQdl_4u2A1XxVgtvoEcuGJWyVJ")
# public_url =  ngrok.connect(port_no).public_url


# app = Flask(__name__)
app.secret_key = 'any random string'

@app.route('/', methods=['GET', 'POST'])
def rootpage():
    return render_template('index.html')

@app.route('/nlp', methods=['GET', 'POST'])
def nlppage():
    nlp = ''
    num_results = 0
    if request.method == 'POST' and 'searchwords' in request.form:
        num_results, nlp = stem_and_vectorize_products_based_on_metadata(request.form.get('searchwords')) 
    return render_template('nlp.html',
                           nlp=nlp, 
                           num_results=num_results)

@app.route('/svd', methods=['GET', 'POST'])
def svdpage():
    print("1")
    svd_recs = ''
    print("2")
    num_results = 0
    print("3")
    session['n_left_to_rate'] = None
    print(request.method == 'POST')
    print(request.form.get('num_to_rate'))
    if (request.method == 'POST') and ('num_to_rate' in request.form):
        print("5")
        session['rate_aisle'] = request.form.get('rate_aisle')
        print("6")
        session['n_to_rate'] = float(request.form.get('num_to_rate'))
        print("7")
        session['rec_aisle'] = request.form.get('rec_aisle')
        print("10")
        session['n_to_rec'] = float(request.form.get('num_to_rec'))
        print("11")
        session['percent_diverse'] = float(request.form.get('diversity_index'))
        print("12")
        session['prod_name'], session['prod_aisle'], session['prod_id'] = get_sample_product(session['rate_aisle'])
        print("13")
        session['n_left_to_rate'] = session['n_to_rate']-1
        print("14")
        session['ratings_list'] = []
        print("15")
        return render_template('rating.html')
    else:
        print("16")
        print(request.method=='POST')
        print(request.form.get('num_to_rate'))
        # return render_template('rating.html')
        return render_template('svd.html',
                            svd_recs=svd_recs,
                            num_results=num_results)                                                                                                                   
                        
@app.route('/rating', methods=['GET', 'POST'])
def ratingpage():
    try:
        if session['n_to_rate'] == None:
            return render_template('svd.html',
                                    svd_recs='',
                                    num_results=0)     
        
        if session['n_left_to_rate'] == 0:
            ranked_products = generate_recs(session['ratings_list'], session['n_to_rec'], session['percent_diverse'], rec_aisle=session['rec_aisle'])
            print("check length of ranked_products: ",len(ranked_products))
            num_results, svd_recs = recommend_diverse_products(ranked_products, session['n_to_rec'], aisle=session['rec_aisle'], percent_diverse=session['percent_diverse'])
            return render_template('svd.html', svd_recs=svd_recs,num_results=num_results)
        elif 'rate_product' in request.form:
            rating = float(request.form.get('rate_product'))
            session['ratings_list'].append([session['prod_id'], rating])
            session['n_left_to_rate'] -= 1
            session['prod_name'], session['prod_aisle'], session['prod_id'] = get_sample_product(session['rate_aisle'])
            return render_template('rating.html')
        else:
            return render_template('rating.html')  
    except:
        return render_template('svd.html',
                                svd_recs='',
                                num_results=0)   


# if __name__ == "__main__":
#     app.run(debug=True)
# public_url = public_url[:4] + "s" + public_url[4:]
# print(f"To acces the Gloable link please click {public_url}")
app.run(port=port_no)