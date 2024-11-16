# AI-Shopping-Cart Project

## Overview

The **AI-Shopping-Cart** is an advanced, AI-driven e-commerce platform designed to revolutionize online shopping. By leveraging machine learning models, semantic search, and a streamlined backend, it offers:

- Personalized product recommendations.
- Robust user activity tracking.
- Dynamically updated product rankings and semantic search capabilities.
- Improved shopping cart and checkout experience.

This system integrates multiple roles and functionalities to enhance user experience while providing comprehensive tools for developers and administrators.

---

## Table of Contents

1. [Contributors](#contributors)
2. [Installation Requirements and Steps](#installation-requirements-and-steps)
3. [Usage](#usage)
4. [Recent Major Changes](#recent-major-changes)
5. [Features and Modules](#features-and-modules)

---

## Contributors

### By Name

- **Dominic Digiacomo**: Scrum Master, Co-Lead Front-End Engineer, Administration and Coordination Specialist
- **Navya Bade**: Co-Lead Front-End Engineer
- **Mariam Lafi**: Product Owner & Secondary Database Engineer
- **Talon Jasper**: Secondary Back-End Engineer & Secondary Front-End Engineer
- **Nya James**:  Co-Lead Database Engineer & Secondary Back-End Engineer 
- **Jakub Bartkowiak**: Lead ML/AI Engineer, Back-End Engineer, Co-Lead Database Engineer, Backend/Database integration Specialist

### By Role

#### Database Engineering
- **Mariam Lafi**: Assisted in database engineering tasks, supporting Jakub Bartkowiak in setting up tables and basic configurations.
- **Nya James**: Provided additional support in database-related engineering, focusing on maintenance and troubleshooting.
- **Jakub Bartkowiak**: Co-Lead Database Engineer, responsible for designing the database schemas, creating entirety of synthetic data, and developing the CSV to database import script, as well as validating frontend/backend compatibility

#### Front-End Engineering
- **Navya Bade**: Lead Front-End Engineer, responsible for the development and maintenance of the user-facing components of the application.
- **Talon Jasper**: Assisted in front-end tasks, working closely with Navya on specific feature implementations.

#### Back-End Engineering
- **Talon Jasper**: Assisted in backend tasks, focusing on specific modules and endpoint implementation.
- **Nya James**: Assisted in backend engineering, supporting development and maintenance efforts.
- **Jakub Bartkowiak**: Back-End Engineer, responsible for server-side logic, input validation, and search functions.

#### Machine Learning/AI
- **Jakub Bartkowiak**: Lead ML/AI Engineer, responsible for designing and integrating all machine learning models and AI-driven functionalities, including semantic search and recommendation systems.

#### General Engineering
- **Dominic Digiacomo**: Contributed to general engineering tasks, helping coordinate between different engineering roles. Key role in organizing team and workloads

#### Administration
- **Dominic Digiacomo**: Scrum Master, facilitated agile ceremonies and ensured that the project was on track.
- **Mariam Lafi**: Product Owner, managed product requirements and ensured alignment with user needs.

---

## Installation Requirements and Steps

### Cloning the Repository

```bash
git clone https://github.com/DominicD213/AI-Shopping-Cart.git
```

### Installing Dependencies

Navigate to the project directory and install required packages:

```bash
pip install -r requirements.txt
```

### MySQL Setup

1. Install MySQL: [Download from MySQL](https://dev.mysql.com/downloads/).
2. Start MySQL Server:
   - Windows: `net start MySQL`
   - macOS: `brew services start mysql`
   - Linux: `sudo service mysql start`
3. Database Initialization:
   - Log into MySQL: `mysql -u root -p`
   - Create database and user:

   ```sql
   CREATE DATABASE shopping_cart;
   CREATE USER 'shop_admin'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON shopping_cart.* TO 'shop_admin'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Environment Variables

Create a `.env` file in the root directory:

```
# Flask Secret Key
SECRET_KEY=your_flask_secret_key

# MySQL Configuration
MYSQL_USER=shop_admin
MYSQL_PASSWORD=secure_password
MYSQL_HOST=localhost
MYSQL_DB=shopping_cart
MYSQL_PORT=3306
```

Add `.env` to `.gitignore` to secure sensitive information.

---

## Usage

Start the application:

```bash
flask run
```

Alternatively:

```bash
python app.py
```

---

## Recent Major Changes

### app.py

- **v0.6-v0.8 (11/10 to 11/12/24 - Jakub Bartkowiak)**:
  - Introduced CartItem and OrderItem endpoints.
  - Enhanced API error handling for scalability.
  - Improved session token validation.

### models.py

- **v1.0-v1.3 (11/15 to 11/17/24 - Jakub Bartkowiak)**:
  - Enhanced ProductEmbedding model for flexible embeddings.
  - Added price, discount, and was_price fields for products.
  - Improved dimension tracking for embedding flexibility.

### search.py

- **v0.9-1.0 (11/16-11/17/24 - Jakub Bartkowiak)**:
  - Added support for dynamic embeddings (50D and 300D).
  - Improved filtering for price, rating, and categories.
  - Enhanced query parsing for user searches.

---

## Features and Modules

### Core Functionality

- **User Management**:
  - Secure login/logout with JWT authentication.
  - Role-based access control for admins.

- **Product Management**:
  - Dynamic product embeddings for advanced semantic search.
  - Flexible embedding sizes (50D for testing, 300D for production).

- **Search and Recommendations**:
  - Multi-modal semantic search using embeddings.
  - Personalized recommendations based on user activity.

- **Cart and Checkout**:
  - Cart management APIs with validation.
  - Seamless checkout integration.

### Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: MySQL
- **AI/ML**: NumPy, SciKit-Learn
- **Frontend**: React.js (integrated via CORS)

### Additional Modules

- **Activity Tracking**: Records user interactions for analytics.
- **Validation**: Input validation with spell checking and prohibited keyword filtering.
<<<<<<< HEAD
- **Testing**: Modular test cases for API endpoints and semantic search.
=======
- **Testing**: Modular test cases for API endpoints and semantic search.
>>>>>>> d41b7f2 (Update README.md)
