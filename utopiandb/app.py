#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import os
import math
from .mongostorage import MongoStorage
from .config import ENTRIES_PER_PAGE

app = Flask(__name__)
m = MongoStorage()

@app.context_processor
def my_utility_processor():
    def add_to_request(key, value):
        baseurl =  request.path+"?"
        for arg in request.args:
            if arg == key:
                baseurl += "&%s=%s" % (key, value)
            else:
                baseurl += "&%s=%s" % (arg, request.args[arg])
        if key not in request.args:
            baseurl += "&%s=%s" % (key, value)
        return baseurl

    def remove_from_request(key):
        baseurl =  request.path+"?"
        for arg in request.args:
            if arg == key:
                continue
            else:
                baseurl += "&%s=%s" % (arg, request.args[arg])
        return baseurl

    return dict(add_to_request=add_to_request,
                remove_from_request=remove_from_request)

@app.route('/')
def index():
    page = request.args.get('page', default = 1, type = int)
    contrib_type = request.args.get('type', default = None, type = str)
    contrib_repo = request.args.get('repo', default = None, type = str)
    contrib_author = request.args.get('author', default = None, type = str)
    contrib_voted = request.args.get('voted', default = None, type = str)
    contrib_title = request.args.get('title', default = None, type= str)

    conditions = {}
    if contrib_type:
        conditions['type'] = contrib_type
    if contrib_repo:
        conditions['repo'] = contrib_repo
    if contrib_author:
        conditions['author'] = contrib_author
    if contrib_voted:
        if contrib_voted.lower() == "true":
            conditions['voted'] = True
        else:
            conditions['voted'] = False
    if contrib_title:
        conditions['title'] = {"$regex": "(?i)%s" % (contrib_title)}

    contrib_count = m.Posts.count(conditions)
    pages = math.ceil(contrib_count / ENTRIES_PER_PAGE)
    start = ENTRIES_PER_PAGE * (page - 1)
    results = m.Posts.find(conditions, limit=ENTRIES_PER_PAGE,
                          skip=start, sort=[('created', -1)])

    content = "<table>"
    for post in results:
        content += render_template("contribution.html", post=post)

    content += "</table>"

    return render_template('index.html', content=content,
                           total_pages=pages, page=page)

if __name__ == '__main__':
    app.run(debug=config.DEBUG, use_reloader=True)
