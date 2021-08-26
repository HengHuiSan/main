from django.http.response import HttpResponse
from django.shortcuts import render
from ecommerce.models import *
import pandas as pd
import numpy as np
# import the class containing the dimensionality reduction method
from sklearn.decomposition import TruncatedSVD

""" GET DATAFRAMES """

def getMergeDf():
    furniture_df = getFurnitureDf()
    user_views_df = getViewDf()

    merge_df = furniture_df.merge(user_views_df, on='furnitureId')
    merge_df = merge_df.drop(columns=['furnitureGenres', 'id'])
    
    return merge_df

def getFurnitureDf():
    furniture_df = pd.DataFrame(list(Furniture.objects.all().values()))
    furniture_df = furniture_df.drop(columns=['furnitureImg', 'unitPrice', 'categoryId_id', 'stock'])

    return furniture_df

def getViewDf():
    user_views_df = pd.DataFrame(list(User_Views.objects.all().values()))
    user_views_df.rename(columns={'furnitureId_id':'furnitureId', 'userId_id':'userId'}, inplace=True)

    return user_views_df

"""
PART 1: Recommend Popular Items to New Users 

"""

"""
PART 2: Recommend Items to Users Who Has NO Purchased History

"""





"""
 PART 3: Recommend Items to Users Who Has Purchased History

 Model-based collaborative filtering using Matrix Factorization
 based on customer's purchase history and 
 page views by other users who views items similar items

 Content-based filtering by weighting genres of furniture

"""    
# Inspired by your browsing history
def contentBasedFiltering(uid):
    furniture_df = getFurnitureDf()
    furniture_df['furnitureGenres'] = furniture_df.furnitureGenres.str.split('|')

    furniture_with_genres = furniture_df.copy(deep=True)

    # Iterating through furniture_df, append 1 if that product's genres contain that genre
    for index, row in furniture_df.iterrows(): # iterrows(): iterate over DataFrame rows
        for desc in row['furnitureGenres']:
            furniture_with_genres.at[index, desc] = 1   
    
    # Filling in the NaN values with 0 to show that furniture doesn't have that column's genre
    furniture_with_genres = furniture_with_genres.fillna(0)

    all_user_profile_df = getViewDf()
    target_user_profile = all_user_profile_df[all_user_profile_df['userId'] == uid]
    target_user_profile = target_user_profile.merge(furniture_df, on='furnitureId').drop(columns=['id', 'furnitureGenres'])

    # Create furniture matrix 
    profile_with_desc = furniture_with_genres[furniture_with_genres.furnitureId.isin(target_user_profile.furnitureId)]
    profile_with_desc.reset_index(drop=True, inplace=True)
    profile_with_desc = pd.DataFrame(profile_with_desc.drop(columns=['furnitureId', 'furnitureName', 'furnitureGenres']))


    view_df = pd.DataFrame(target_user_profile.drop(columns=['userId','furnitureId','furnitureName']))
    # view_df = pd.DataFrame(target_user_profile.drop(columns=['userId_id', 'furnitureName']))

    print(User.objects.get(id=4).username)
    print(profile_with_desc.shape)
    print(view_df.shape)

    # Multiply furniture matrix with view_df to get weighted genres matrix
    user_profile = profile_with_desc.T.dot(view_df) 
    # user_profile = pd.DataFrame(user_profile / user_profile.values.sum())
    print(user_profile.shape)

    furniture_with_genres = furniture_with_genres.set_index(furniture_with_genres.furnitureId)
    furniture_with_genres = furniture_with_genres.drop(columns=['furnitureId', 'furnitureName', 'furnitureGenres'])
    print(furniture_with_genres.shape)
    # furniture_with_genres = furniture_with_genres.drop(columns=['furnitureName', 'furnitureGenres'])

    # Multiply furniture matrix (not active user) with weighted genres matrix to generate recommendation 
    recommend_furniture = furniture_with_genres.dot(user_profile)
    recommend_furniture = pd.DataFrame(recommend_furniture / recommend_furniture.values.sum())

    print(recommend_furniture.shape)
    recommend_furniture = recommend_furniture[recommend_furniture['viewCount'] != 0]
    recommend_furniture.sort_values(by=['viewCount'], ascending=False, inplace=True)

    # List out recommended items
    recommend_list = list(recommend_furniture.index)

    # # Remove similar items from CF-generated list
    collaborative_rec_list = collaborativeFiltering(uid)
    recommend_items = []
    for j in collaborative_rec_list:
        for i in recommend_list:
            if j != i:
                recommend_items.append(i)

    return recommend_items


# Top picks for you
def collaborativeFiltering(uid):
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

    # Get all the orders that made by target user from 'Order' table
    oid_list = list(Order.objects.filter(userId=uid).values_list('orderId', flat=True)) # flat=True : mean that the returned result is a single value, not a tuple. 

    # Get all items from the order list of target user
    all_items_purchased_list = list(Order_Products.objects.values_list('orderId', 'furnitureId'))

    # List out all items from each order
    items_purchased = []
    for oid in oid_list:
        for i in range(len(all_items_purchased_list)):
            if oid == all_items_purchased_list[i][0]:
                items_purchased.append(all_items_purchased_list[i][1])

    # Isolating items purchased by the active user from Correlation Matrix
    for i in items_purchased:
        for j in range(len(items_users_pivot_matrix_df)):
            if(items_users_pivot_matrix_df.index[j] == i):
                # print(items_users_pivot_matrix_df.index[j])
                fid_list = list(items_users_pivot_matrix_df.index) # change everything into list form
                
                # find the index(location) of the target item
                item_purchased = fid_list.index(i)
                
                # get correlation coefficients value of the item
                correlation = correlation_matrix[item_purchased]
                
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


# Trending now
def popularityBasedFiltering():
    user_profile_df = getViewDf()

    popular_items = user_profile_df.groupby('furnitureId')['viewCount'].count()
    popular_items = pd.DataFrame(popular_items)
    most_popular_items = popular_items.sort_values(by=['viewCount'], ascending=False)
    
    recommend_list = list(most_popular_items.index)

    return recommend_list
