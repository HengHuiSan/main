<h1 align="center" id="title">Recommendation System For Online Pre-Owned Furniture Store With Machine Learning </h1>


## Table of Contents

- [🚀 Demo](#demo)
- [🗒️ Project Overview](#project-overview)
- [🛠️ Project Scope](#project-scope)
- [💻 Installation](#installation)

## 🚀 Demo

### Furniture Store



https://github.com/henghuisan/furniture-store-recommendation-system/assets/76814491/c418b750-101b-44d5-b8f3-493fdc04aaec



<br />

### Admin Dashboard


https://github.com/henghuisan/furniture-store-recommendation-system/assets/76814491/28a5eb7b-0dba-4db3-b8bb-7c4eda15b3e9


---

## 🗒️Project Overview

This project delivers personalized recommendations for three user types:

- **New Users**: Recommendations for users with no browsing or purchase history.
- **Users with No Purchase History (Normal User)**: Recommendations for users who have browsed items but haven't made purchases.
- **Users with Purchase History (Customer)**: Recommendations for users based on their purchase history.

### Recommendation Strategies
After identifying the user type, the recommendation system applys various filtering techniques.

#### Part 1: Recommend Popular Items to New Users

- **Hot Products**
   
   Popularity-based filtering using view counts to generate top-viewed item recommendations.

#### Part 2: Recommend Items to Users with No Purchased History

- **Inspired by Your Browsing History**
   
   Model-based collaborative filtering using TruncatedSVD, considering active user's page views and similar item views by other users.

- **Hot Products**
  
  Popularity-based filtering using view counts to generate top-viewed item recommendations.

#### Part 3: Recommend Items to Users with Purchased History

- **Because You Bought ...**
   
   Content-based filtering using customer's purchase history and item features to generate item-item recommendations.

- **Inspired by Your Browsing History**
   
   Model-based collaborative filtering using TruncatedSVD, incorporating customer's purchase history and similar item views.

- **Hot Products**
  
  Popularity-based filtering using view counts to generate top-viewed item recommendations.

### Recommendation System Implementation using Google Colab

To delve into the technical aspects of the project, you can explore the Google Colab Notebook where showcases the implementation of these recommendation system techniques: 
- [Furniture Store Recommendation System](https://colab.research.google.com/drive/1L4tgE0Fa2xgk8ou5gHzzf_ydAuRsgwLp?usp=sharing)

---
 
## 🛠️ Project Scope

### 1. Target Users

- Consumer
- Admin

### 2. Functionality

<table>
  <tr>
    <th></th>
    <th>Consumer</th>
    <th>Admin</th>
  </tr>
  <tr>
    <td>
     <b>E-commerce</b> <br />
      ▪	Login and Registration <br />
      ▪	Update Profile Settings <br />
      ▪	Browse Landing Page <br />
      ▪	Browse Product Listing <br />
      ▪	Shopping Cart Access <br />
      ▪	Make Order <br />
      ▪	Make Payment <br />
      ▪	Make Furniture Donation <br />
    </td>
    <td align="center">✅</td>
    <td align="center">✅</td>
  </tr>
  <tr>
    <td>
        <b>Admin Dashboard Management</b> <br/>
        ▪	Login <br/>
        ▪	Product Management <br/>
        ▪	Order Management <br/>
        ▪	Furniture Donation Management <br/>
    </td>
    <td align="center">❌</td>
    <td align="center">✅</td>
  </tr>
</table>

---

## 💻 Installation

### 1. Prerequisites
Before you begin, ensure that you have the following software versions installed:

- [Python](https://www.python.org/downloads/) version **3.9.5** or above
- [MySQL](https://dev.mysql.com/downloads/) version **8** or above

### 2. Clone the Repository
Clone this repository to your local machine using:

```bash
git clone https://github.com/henghuisan/furniture-store-recommendation-system.git
```
### 3. Create a Virtual Environment
Navigate to the cloned directory:

``` bash
cd furniture-store-recommendation-system
```

Create a virtual environment:

- On macOS and Linux:
``` bash
python3 -m venv venv
source venv/bin/activate
```

- On Windows:
``` bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 5. Create a `.env` File
In the root directory of the project, create a file named `.env`.

### 6. Define Environment Variables
Inside the `.env` file, define the necessary environment variables using the following format:

```plaintext
MYSQL_DB_NAME=your_database_name
MYSQL_DB_USER=your_database_username
MYSQL_DB_PASSWORD=your_database_password
MYSQL_DB_HOST=your_database_host
MYSQL_DB_PORT=your_database_port
```
### 7. Importing Existing Data to Database
Download the SQL script - [furniture_store.sql](furniture_store.sql)

Open your web browser and navigate to your phpMyAdmin dashboard. This is typically accessed by visiting `http://localhost/phpmyadmin` if you're working locally or the URL provided by your hosting provider.

Create database and name it as `furniture_store`

Choose the Import Tab and upload the `furniture_store.sql`

### 8. Apply Migrations
Apply database migrations to set up the database schema:
```bash
python manage.py migrate
```

### 9. Create Superuser
Create a superuser account for accessing the admin panel:
```bash
python manage.py createsuperuser
```

### 10. Run the Development Server
Start the development server and run the app:
```bash
python manage.py runserver
```

You should now be able to access the app.
- ecommerce: http://127.0.0.1:8000/user/login/ 
  - register and login using your accounr
- ecommerce admin dashboard: at http://127.0.0.1:8000/admin/login/
  - username: furnishh_admin
  - password: fpassword123
- django admin dashboard: at http://127.0.0.1:8000/django-admin/login/
  - login using your superuser account

