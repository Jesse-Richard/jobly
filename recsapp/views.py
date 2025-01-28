from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from recsapp.forms import LogForm, filterForm

import sqlite3
import json
import subprocess
from django.conf import settings
import os

# Create your views here.
def home(request):
    return render(request, '_index.html')

def about(request):
    return render(request, 'about.html')

def results(request):
    return render(request, 'results.html')

def inputForm(request):
    form = LogForm()
    if request.method == 'POST':
        form = LogForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'form.html', context)

#
##
### User-Generated Data
USERDATA = os.path.join(settings.MEDIA_ROOT, 'recommendations.json')
shared_data = {}
###
##
#

def submitFilter(request):
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    table_name = 'recsapp_logger'
    json_file_path = USERDATA

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = f'SELECT id, skills, workexp FROM {table_name} ORDER BY id DESC LIMIT 1'

        cursor.execute(query)
        row = cursor.fetchone()

        if row:
            data = {"id": row[0], "skills":row[1], "experience":row[2]}
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            
        else:
            return JsonResponse({"status": "error", "message": "No data found in the database"}, status=404)
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    finally:
        if conn:
            conn.close()
        
        form = filterForm()

        if request.method == 'GET' and 'country' in request.GET and 'salary' in request.GET:
            form =filterForm(request.GET)

            if form.is_valid():
                shared_data['filter_data'] = form.cleaned_data
        
        else:
            form = filterForm(initial=shared_data.get('filtered_data', {}))

        context = {"filter": form}

        return render(request, 'fullfilter.html', context)
    

# def another_function():
#     print("Filter Data:", shared_data.get('filter_data', {}))
#     # Use the shared data

# script_path = os.path.join(settings.BASE_DIR, 'the_script')


RUNSKILLS = os.path.join(settings.BASE_DIR, 'model/bash', 'run_skills.sh')
RUNWORKEXP = os.path.join(settings.BASE_DIR, 'model/bash', 'run_workex.sh')


def processing(request):
    try:
        subprocess.run(['C:\\Program Files\\Git\\bin\\bash.exe', RUNSKILLS, USERDATA], check=True)
    except subprocess.CalledProcessError as e:
            return JsonResponse({"status": "error", "message": f"Script execution failed: {e}"}, status=500)
    
    try:
        subprocess.run(['C:\\Program Files\\Git\\bin\\bash.exe', RUNWORKEXP, USERDATA], check=True)
    except subprocess.CalledProcessError as e:
            return JsonResponse({"status": "error", "message": f"Script execution failed: {e}"}, status=500)
    
    return render(request, 'processing.html')

# try:
#     subprocess.run([script_path, json_file_path], check=True)
#     return JsonResponse({"status": "success", "message": "Script executed Successfully", "data": data})
# except subprocess.CalledProcessError as e: 
#         return JsonResponse({"status": "error", "message": f"Script execution failed: {e}"}, status=500)