from django.http.response import HttpResponse
from ecommerce.models import *
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from collections import Counter


"""
PART 1: Recommend Popular Items to New Users 

a) Hot Products : 
   Popularity-based filtering based on view count of the items
   to generate the most-viewed item recommendations

"""
def recommendToNewUser():
    popularity_recommend_list = popularityBasedFiltering()

    return popularity_recommend_list


"""
PART 2: Recommend Items to Users Who Has NO Purchased History

 a) Inspired by your browsing history :
    Model-based collaborative filtering using Matrix Factorization
    based on active user's page views and  page views by 
    other users who views items similar items

 b) Hot Products

"""
def recommendToNormalUser(uid, role):
    cf_recommend_list = collaborativeFiltering(uid, role)
    popularity_recommend_list = popularityBasedFiltering()
    return cf_recommend_list, popularity_recommend_list


"""
 PART 3: Recommend Items to Users Who Has Purchased History

 a) Because you bought ... :
    Content-based filtering based on customer's purchase history 
    and item features to generate item-item recommendations

 b) Inspired by your browsing history :
    Model-based collaborative filtering using Matrix Factorization
    based on customer's purchase history and page views by
    other users who views items similar items

 c) Hot Products

"""   
def recommendToCustomer(uid, role):
    cb_recommend_list, furniture_name = contentBasedFiltering(uid)
    cf_recommend_list = collaborativeFiltering(uid, role)
    popularity_recommend_list = popularityBasedFiltering()

    return cb_recommend_list, furniture_name, cf_recommend_list, popularity_recommend_list


""" Get Dataframes """

def getMergeDf():
    furniture_df = getFurnitureDf()
    user_views_df = getViewDf()

    merge_df = furniture_df.merge(user_views_df, on='furnitureId')
    merge_df = merge_df.drop(columns=['furnitureGenres', 'id'])
    
    return merge_df

def getFurnitureDf():
    furniture_df = pd.DataFrame(list(Furniture.objects.all().values()))
    furniture_df = furniture_df.drop(columns=['furnitureImg', 'unitPrice', 'categoryId_id', 'stock', 'slug'])

    return furniture_df

def getViewDf():
    user_views_df = pd.DataFrame(list(User_Views.objects.all().values()))
    user_views_df.rename(columns={'furnitureId_id':'furnitureId', 'userId_id':'userId'}, inplace=True)

    return user_views_df
    

""" Content-based Filtering Recommendation """  

def contentBasedFiltering(uid):
    furniture_df = getFurnitureDf()
    furniture_df['furnitureGenres'] = furniture_df.furnitureGenres.str.split('|')

    # Use Counter to create a dictionary containing frequency counts of each genre
    genres_counts = Counter(g for genres in furniture_df['furnitureGenres'] for g in genres)
    
    # Iterating through furniture_df, append 1 if that furniture's genres contain that genre, while "0" does not
    genres = list(genres_counts.keys())
    for g in genres:
        furniture_df[g] = furniture_df['furnitureGenres'].transform(lambda x: int(g in x))

    # furniture_matrix = furniture_df[genres].copy(deep=True)

    # Build item-item recommendation using cosine similarity
    cosine_sim = cosine_similarity(furniture_df[genres], furniture_df[genres])
    # print(f"Dimensions of our movie features cosine similarity matrix: {cosine_sim.shape}")

    items_purchased = getSpecificOrderItems(uid)

    # create index mapper which maps furniture ID to the index that it represents in the matrix
    furniture_idx = dict(zip(furniture_df['furnitureId'], list(furniture_df.index)))

    furniture_name = []
    recommend_list = []

    for i in items_purchased:
        fid = furniture_idx[i.furnitureId.furnitureId]
        
        # Add counter to the list e.g. [(0, 'a'), (1, 'b'), (2, 'c')]
        sim_scores = list(enumerate(cosine_sim[fid]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Get top 100 most similar items to target item.
        sim_scores = sim_scores[:100]
        # Get the row index
        similar_furniture = [i[0] for i in sim_scores]

        # remove items that viewed before in the list
        items = list(furniture_df['furnitureId'].iloc[similar_furniture])
        recommend_furniture = removeViewedItem(uid,items)

        # recommend_list.append(list(furniture_df['furnitureId'].iloc[similar_furniture]))
        recommend_list.append(recommend_furniture[:12])
        furniture_name.append(i.furnitureId.furnitureName)
    
    # print(recommend_list)

    return recommend_list, furniture_name

def removeViewedItem(uid,similar_items):
    item_viewed = getAllViewedItems(uid)

    # print("viewed Item")
    # print(len(item_viewed))

    # print("similar_items ")
    # print(len(similar_items))

    for i in item_viewed:
        for j in similar_items:
            if i == j:
                similar_items.remove(j)

    # print("similar_items ")
    # print(len(similar_items))
    
    return similar_items


def getSpecificOrderItems(uid):
    # Get all the orders that made by target user from 'Order' table
    oid_list = Order.objects.filter(userId=uid) 
    latest_order = oid_list.latest('orderDate') 

    # Get all items from the target order
    items_purchased = Order_Products.objects.filter(orderId=latest_order).all()

    return items_purchased


""" Collaborative Filtering Recommendation """  

def collaborativeFiltering(uid,role):   
    furniture_profile_df = getMergeDf()

    #Creating a sparse pivot table with items in rows and users in columns
    users_items_pivot_matrix_df = furniture_profile_df.pivot_table(index='userId', columns='furnitureId', values='viewCount').fillna(0)

    # Transposing the matrix
    items_users_pivot_matrix_df = users_items_pivot_matrix_df.T

    # Decomposing the Matrix
    SVD = TruncatedSVD(n_components=10) # n_components=10: final number of dimensions

    # Fit the instance on the data and then transform the data
    decomposed_matrix = SVD.fit_transform(items_users_pivot_matrix_df)

    # Compute correlation coefficients 
    correlation_matrix = np.corrcoef(decomposed_matrix)

    item_list = getAllOrderItems(uid) if role == "customer" else getAllViewedItems(uid)

    # Isolating items purchased by the active user from Correlation Matrix
    for i in item_list:
        for j in range(len(items_users_pivot_matrix_df)):
            if(items_users_pivot_matrix_df.index[j] == i):
                # print(items_users_pivot_matrix_df.index[j])
                fid_list = list(items_users_pivot_matrix_df.index) # change everything into list form
                
                # find the index(location) of the target item
                item = fid_list.index(i)
                
                # get correlation coefficients value of the item
                correlation = correlation_matrix[item]
                
                # list out items that the pearson correlation value > 0.9 
                # 0.9 suggests a strong, positive association between two variables 
                recommend_list = list(items_users_pivot_matrix_df.index[correlation > 0.90])
                
                # remove the items already bought by the active user
                recommend_list.remove(i) 

                # sort items with the highest pearson correlation value
                recommend_list.sort(reverse=True)

                # get the first 12 items
                recommend_list = recommend_list[:12]
       
    return recommend_list


def getAllOrderItems(uid):
    # Get all the orders that made by target user from 'Order' table
    oid_list = list(Order.objects.filter(userId=uid).values_list('orderId', flat=True)) # flat=True : mean that the returned result is a single value, not a tuple. 

    # Get all items from the order list of target user
    all_items_purchased_list = list(Order_Products.objects.values_list('orderId', 'furnitureId'))
    print(all_items_purchased_list)

    # List out all items from each order
    items_purchased = []
    for oid in oid_list:
        for i in range(len(all_items_purchased_list)):
            if oid == all_items_purchased_list[i][0]:
                items_purchased.append(all_items_purchased_list[i][1])
    
    return items_purchased

def getAllViewedItems(uid):
    item_viewed = list(User_Views.objects.filter(userId=uid).values_list('furnitureId', flat=True))

    return item_viewed


""" Popularity-based Filtering Recommendation """  

def popularityBasedFiltering():
    user_profile_df = getViewDf()

    popular_items = pd.DataFrame(user_profile_df.groupby('furnitureId')['viewCount'].count())
    most_popular_items = popular_items.sort_values(by=['viewCount'], ascending=False)
    
    recommend_list = list(most_popular_items.index)
    recommend_list = recommend_list[:8]

    return recommend_list
