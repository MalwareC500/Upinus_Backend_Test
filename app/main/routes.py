#!/usr/bin/python
# -*- coding: utf8 -*-

from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import LoginForm
import datetime
import os
from .utils import process

P = process()


@main.route('/', methods=['GET', 'POST'])
def index():
    return "hello"

@main.route('/upload', methods=['POST'])
def upload_file():
    uploaded_files = request.files
    # checking if the files (stock, priority, order lists) is present or not.
    if 'stock_file' not in uploaded_files:
        return "Wrong arguments"
    if 'priority_file' not in uploaded_files:
        return "Wrong arguments"
    if 'order_list_file' not in uploaded_files:
        return "Wrong arguments"

    # create folder to save new order files

    dname = str(datetime.datetime.now())
    os.mkdir('static/' + dname)

    order_dir = "static/" + dname

    # save files
    stock_file = uploaded_files['stock_file']
    stock_file_add = os.path.join(order_dir, "stock.csv")
    stock_file.save(stock_file_add)

    priority_file = uploaded_files['priority_file']
    priority_file_add = os.path.join(order_dir, "priority_file.csv")
    priority_file.save(priority_file_add)

    order_list_file = uploaded_files['order_list_file']
    order_list_file_add = os.path.join(order_dir, "order_list_file.csv")
    order_list_file.save(order_list_file_add)
    print("file successfully saved")
    output_file = P.process_order(stock_file_add, priority_file_add, order_list_file_add, order_dir)
    return output_file

