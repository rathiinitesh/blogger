from blogger import app

"""
The email and password were set as Environment variables for obvious reason and thus to send emails for password 
reset request either set environment variables or hard code them, eitherway check the __init__.py file in blogger
package for the enviornment variable names. Do the same for the secret key for the app. 
"""

if __name__ == '__main__':
    app.run(debug=True)
