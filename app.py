from bike_sharing_app import app
from flask import Flask, render_template, redirect, url_for, request

if __name__ == "__main__":
    app.run(debug=True)
