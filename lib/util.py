"""=============================================================================
util.py

General Unilities for the Web App
============================================================================="""
# =========
#  Imports  
# =========
# ---------------
# Python Imports
# ---------------
import csv
import datetime
import json
import operator
import re # Regular Expression operations
import StringIO
import sys,os
import tempfile,zipfile

# ---------------
# Django Imports
# ---------------
from django.conf import settings
from django.core.servers.basehttp import FileWrapper # Wrap large files for zip download
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext

# --------------------
# Application Imports
# --------------------
## Settings attributes
from OutcomesStrategiesManagementApp.settings import SERVER_URL,ROOT_URL,APP_SERVER_URL

# ------------------------
# Third Party Libs Import
# ------------------------
## Import psycopg2 for PostgreSQL database connection
import psycopg2

## Import the ElementTree XML API for Python
from xml.etree import ElementTree

## Import xlrd for reading XLS files with Python
from xlrd import open_workbook


# =================
# GLOBAL VARIABLES 
# =================

# Server App Root
## use this for [LOCALHOST] -> ******************************************!!!->
SERVER_APP_ROOT = ""
## <- use this for [LOCALHOST]

## use this for [SERVER] ->
#SERVER_APP_ROOT = "/outcomesandstrategiesmanagement"
## <- use this for [SERVER] ********************************************<-!!!

# Admin email
ADMIN_EMAIL_ADDRESS = "outcomesandstrategiesmanagement@gmail.com"
## use this for [LOCALHOST] -> ******************************************!!!->
TO_EMAIL_ADDRESS = ["liu.qing.1984@gmail.com"]
TO_DE_ADMIN_EMAIL_ADDRESS = ["liu.qing.1984@gmail.com"]
## <- use this for [LOCALHOST]
## use this for [SERVER] ->
#TO_EMAIL_ADDRESS = ["outcomesandstrategiesmanagement+admin@gmail.com","mzhang@piton.org"]
#TO_DE_ADMIN_EMAIL_ADDRESS = ["outcomesandstrategiesmanagement+admin@gmail.com","jnewcomer@piton.org","mzhang@piton.org"]
## <- use this for SERVER ***********************************************<-!!!

# ===========
# Decorators
# ===========
# 'render_to', 
# 'HumanReadableSize', 'GetDirSize', 'GetFileSize', 'GetShapefileSize',
# 'CleanNullValue',
# 'HasPermission',
#============================================================================
# render_to Decorator to save time returning templates
def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response 
    function with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer

# Convert file size to human readable presentation of a number of bytes
def HumanReadableSize(size,precision):
    suffixes = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    suffix_index = 0
    while size >= 1024:
        suffix_index += 1
        size /= 1024.0
    return "%.*f %s" % (precision,size,suffixes[suffix_index])

# Clean NULL value for strings in table when uploading from CSV file
def CleanNullValue(value):
    return NO_DATA_VALUE if value=="" else value

# Get total file size for directory
def GetDirSize(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

# Get file size for all possible extensions
def GetFileSize(file_path,extensions):
    file_size = 0
    for extension in extensions:
        file_full_path = file_path+".%s" % extension
        if os.path.exists(file_full_path):
            file_size = os.path.getsize(file_full_path)
    return file_size

# Get total file size for shapefile and accociated files (.shp,.dbf,.prj,.sbn,.sbx,.shp.xml,.shx)
def GetShapefileSize(file_path):
    file_size = 0
    for extension in SHAPEFILE_EXTENSION:
        file_full_path = file_path+".%s" % extension
        if os.path.exists(file_full_path):
            file_size += os.path.getsize(file_full_path)
    return file_size

# Check user permissions
def HasPermission(user,app,perm,model):
    return user.has_perm('%s.%s_%s' % (app,perm,model))