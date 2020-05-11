from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
# from .forms import LoginForm

user_bp = Blueprint('user_bp', __name__,
                      template_folder='templates', static_folder='static')