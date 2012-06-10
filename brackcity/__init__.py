from flask import Flask
app = Flask(__name__)
app.config.from_object('brackcity.config')
import brackcity.api_views
