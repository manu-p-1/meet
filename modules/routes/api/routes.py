from server import mysql
from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from server import client
from modules.simulation.logic import department_alloc,department_utilization

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/dept_allocation/', methods=['GET'])
def dept_allocation():

