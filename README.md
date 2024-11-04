<<<<<<< HEAD
=======
<h1 align="center">AI-Shopping-Cart</h1>
>>>>>>> main

<h1 align="center"><strong>AI-Shopping-Cart Project</strong></h1>

<p align="center">
    The <strong>AI-Integrated Shopping Management System</strong> is an AI-powered software solution designed to enhance the online shopping experience. It provides users with dynamically tailored search results and product recommendations, considering product popularity, ratings, and an improved shopping cart and checkout experience.
</p>

<h2><strong>Table of Contents</strong></h2>
<ol>
    <li><a href="#contributors"><strong>Contributors</strong></a></li>
    <li><a href="#installation-requirements-and-steps"><strong>Installation Requirements and Steps</strong></a></li>
    <li><a href="#usage"><strong>Usage</strong></a></li>
    <li><a href="#recent-changes"><strong>Recent Changes</strong></a></li>
</ol>

<h2 id="contributors"><strong>1. Contributors</strong></h2>

<h3><strong>By Name</strong></h3>
<ul>
    <li><strong>Dominic</strong> - Scrum Master & General Engineer</li>
    <li><strong>Navya</strong> - Front-End Engineer</li>
    <li><strong>Mariam</strong> - Product Owner & Primary Database Engineer</li>
    <li><strong>Talon</strong> - Back-End Engineer & Secondary Front-End Engineer</li>
    <li><strong>Nya</strong> - Back-End Engineer & Secondary Database Engineer</li>
    <li><strong>Jakub</strong> - ML/AI Engineer & Integration [backend-database-AI/ML] Engineer</li>
</ul>

<h3><strong>By Role</strong></h3>

<h4><strong>Database Engineering</strong></h4>
<ul>
    <li><strong>Mariam</strong> - Lead Database Engineer</li>
    <li><strong>Nya</strong> - Assistant Database Engineer</li>
    <li><strong>Jakub</strong> - Backend-Database-AI/ML Integration Engineer</li>
</ul>

<h4><strong>Front-End Engineering</strong></h4>
<ul>
    <li><strong>Navya</strong> - Lead Front-End Engineer</li>
    <li><strong>Talon</strong> - Assistant Front-End Engineer</li>
</ul>

<h4><strong>Back-End Engineering</strong></h4>
<ul>
    <li><strong>Talon</strong> - Lead Back-End Engineer</li>
    <li><strong>Nya</strong> - Assistant Back-End Engineer</li>
    <li><strong>Jakub</strong> - Backend-Database-AI/ML Integration Engineer</li>
</ul>

<h4><strong>Machine Learning / AI</strong></h4>
<ul>
    <li><strong>Jakub</strong> - Lead ML/AI Engineer</li>
</ul>

<h4><strong>General Engineering</strong></h4>
<ul>
    <li><strong>Dominic</strong> - General Engineer</li>
</ul>

<h4><strong>Administration</strong></h4>
<ul>
    <li><strong>Dominic</strong> - Scrum Master</li>
    <li><strong>Mariam</strong> - Product Owner</li>
</ul>

<h2 id="installation-requirements-and-steps"><strong>2. Installation Requirements and Steps</strong></h2>
<p>To install the project, follow these steps:</p>

<h4><strong>Cloning the Repository</strong></h4>
<p>Using your terminal or CLI, clone the repository to your local machine:</p>

```bash
git clone https://github.com/DominicD213/AI-Shopping-Cart.git
```

<h4><strong>Installing Dependencies</strong></h4>
<p>Navigate to the project directory and install the necessary dependencies:</p>

```bash
pip install -r requirements.txt
```

<h4><strong>MySQL Setup</strong></h4>
<p>As a developer, you'll need to have MySQL installed and running to support the application database.</p>
<ol>
    <li><strong>Download and Install MySQL:</strong> Download the installer from the <a href="https://dev.mysql.com/downloads/installer/">MySQL website</a> and follow the installation instructions.</li>
    <li><strong>Start the MySQL Server:</strong> Ensure MySQL is running by starting it from the command line or through your system's services.
        <ul>
            <li><strong>Windows:</strong> Open Command Prompt and run: <code>net start MySQL</code></li>
            <li><strong>macOS (if installed via Homebrew):</strong> Run: <code>brew services start mysql</code></li>
            <li><strong>Linux:</strong> Use: <code>sudo service mysql start</code></li>
        </ul>
    </li>
    <li><strong>Set up the Database:</strong> Log into the MySQL shell and create the necessary database and user:
        <ol>
            <li>Access MySQL: <code>mysql -u root -p</code></li>
            <li>Create the database: <code>CREATE DATABASE my_database;</code></li>
            <li>Create a user and grant permissions:
                <pre>
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON my_database.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
                </pre>
            </li>
        </ol>
    </li>
</ol>

<h4><strong>Environment Variables (.env) Setup</strong></h4>
<p>The project uses a <code>.env</code> file to securely store database credentials and Flask app secrets. This file should be created in the root of your project directory. It is loaded at runtime to provide these values to the application without hardcoding them in the source code.</p>

<p>Here is an example of what your <code>.env</code> file should look like:</p>

```plaintext
# Flask Secret Key for managing sessions
SECRET_KEY=your_flask_secret_key_here

# MySQL Database Credentials
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_DB=your_database_name
MYSQL_PORT=3306
```

<p><strong>Explanation:</strong></p>
<ul>
    <li><code>SECRET_KEY</code>: This is a random string used by Flask to sign session cookies. You can generate a secure key by using Python's <code>os.urandom(24)</code>.</li>
    <li><code>MYSQL_USER</code>, <code>MYSQL_PASSWORD</code>, <code>MYSQL_HOST</code>, <code>MYSQL_DB</code>, <code>MYSQL_PORT</code>: These variables contain the credentials and connection details for your MySQL database. Ensure the database and user exist on your MySQL server, and update these fields with the correct values.</li>
</ul>

<p><strong>Adding MySQL to System PATH:</strong></p>
<p>On some systems, you may need to add the MySQL <code>bin</code> directory to your system PATH to use the <code>mysql</code> command from any terminal or command prompt.</p>
<ol>
    <li><strong>Locate MySQL:</strong> Find the <code>bin</code> directory within your MySQL installation. The path is typically <code>C:\Program Files\MySQL\MySQL Server X.X\bin</code> on Windows.</li>
    <li><strong>Update PATH (Windows):</strong>
        <ul>
            <li>Press <code>Win + R</code>, type <code>sysdm.cpl</code>, and press Enter.</li>
            <li>Under the **Advanced** tab, click **Environment Variables**.</li>
            <li>Find the **Path** variable in **System variables**, click **Edit**, and add your MySQL `bin` directory.</li>
        </ul>
    </li>
</ol>

<p><strong>Note:</strong> Be sure to add your <code>.env</code> file to <code>.gitignore</code> to prevent it from being uploaded to version control, as it contains sensitive information.</p>

```plaintext
# .gitignore
.env
```

<h2 id="usage"><strong>3. Usage</strong></h2>
<p>To start the application, use either of the following commands:</p>

```bash
flask run
```

```bash
python app.py
```

<h2 id="recent-changes"><strong>4. Recent Changes</strong></h2>
<ul>
    <li><strong>v0.3 - 10-14-24 (Jakub Bartkowiak)</strong> - Refactored code to utilize a MySQL connection via SQLAlchemy instead of SQLite. Changed the <code>users</code> table name to <code>user</code> and implemented password hashing with <code>werkzeug.security</code> for enhanced security.</li>
</ul>
