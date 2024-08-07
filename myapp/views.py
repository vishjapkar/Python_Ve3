from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .forms import UploadFileForm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import urllib, base64

def handle_uploaded_file(f):
    try:
        # Try reading the CSV with utf-8 encoding
        df = pd.read_csv(f, encoding='utf-8')
    except UnicodeDecodeError:
        # If utf-8 fails, try with 'latin1' encoding
        f.seek(0)  # Reset file pointer
        df = pd.read_csv(f, encoding='latin1')
    except pd.errors.EmptyDataError:
        raise ValueError("The file is empty or contains no columns to parse.")
    
    return df

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = handle_uploaded_file(request.FILES['file'])
                summary = df.describe().to_html()
                first_rows = df.head().to_html()
                plot_uri = plot_histogram(df)
                return render(request, 'results.html', {'summary': summary, 'first_rows': first_rows, 'plot_uri': plot_uri})
            except ValueError as e:
                return render(request, 'upload.html', {'form': form, 'error': str(e)})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def plot_histogram(df):
    fig, ax = plt.subplots()
    df.hist(ax=ax)
    plt.subplots_adjust(hspace=0.5)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    return uri
