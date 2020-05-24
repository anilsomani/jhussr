# -*- coding: utf-8 -*-
import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.figure_factory as ff
import plotly.graph_objects as go
import math
import textract
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from plotly.tools import mpl_to_plotly

import pandas as pd
from plotly.graph_objs._heatmap import Heatmap

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Co-Occurence Matrix Creator'),

    html.P(['A web application for creating co-occurence matrices based on PDFs and key words entered.', html.Br(), 
        'Author: Shailja Somani', html.Br(),
        'Contact Info: ssomani2@jhu.edu (Pre Aug 2020) OR shailjasomani@gmail.com (Post Aug 2020)']),

    html.H4(children='Please enter the keywords you would like to search for (separated by commas):'),

    dcc.Textarea(
        id='textarea-state-example',
        value='Enter your keywords here',
        style={'width': '100%', 'height': 100},
        ),
    html.Button('Submit', id='textarea-state-example-button', n_clicks=0),
    html.Div(id='textarea-state-example-output', style={'whiteSpace': 'pre-line'}),

    html.H4(children='Please upload the files you would like to search through below (as PDF or Word documents):'),

    html.P(['After you see the message stating which files you have uploaded, please give the program ample ' + 
        'time to process your documents and return the matrix. The more documents you upload, the longer this will take.']),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),

    html.H4(children = 'Final Co-Occurence Matrix:'),

    html.Div(id='errors-info'),

    dcc.Graph(id = 'graph')

])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    try:
        if 'pdf' in filename or 'doc' in filename:
            # Assume that the user uploaded a PDF file
            raw = textract.process(filename)
            text = raw.decode()
            text = text.lower()
            #if 'macromolecules' in text:
               # print('macromolecules found') #Debugging line - only shows up in terminal
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing: ' + filename
        ])
    
    return text

    '''
    return html.Div([html.H5(filename), html.P([text]), html.Hr(), #horizLine
    
        
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df,
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),
        
     
        # For debugging, display the raw contents provided by the web browser
        html.Div(['Raw Content']),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
        
    ])
    '''

def coOccMatrix(numTerms, keyTerms, pdfList):
    # Takes in all key terms, # of terms & list of PDFs as strings.
    # Returns a numerical co-occurence matrix. 
    # Relies on function timesCooccur
    print(numTerms, keyTerms)
    coMatrix = [[0 for x in range(numTerms)] for y in range(numTerms)]
    for i in range(numTerms):
        for j in range(numTerms):
            if keyTerms[i] == keyTerms[j]: 
                coMatrix[i][j] = 0
            else:
                coMatrix[i][j] = timesCooccur(keyTerms[i],keyTerms[j],pdfList)
    print(coMatrix)
    return coMatrix 

def timesCooccur(term1, term2, pdfList):
    #Takes in 2 terms and returns how many strings (in the list stringList) 
    #they are both present in.
    print(term1, term2)
    coOccur = 0
    for k in pdfList: 
        if (term1 in k) and (term2 in k): 
            coOccur = coOccur + 1
    print(coOccur)
    return coOccur
'''
def heatmap_creator(keyTerms, coMatrix):
    fig, ax = plt.subplots(figsize=(10,10))
    heatMap = ax.imshow(coMatrix)
    #fig = ax.matshow(coMatrix)
    
    # Set up & label ticks
    numTerms = len(keyTerms)
    ax.set_xticks(np.arange(numTerms))
    ax.set_yticks(np.arange(numTerms))

    ax.set_xticklabels(keyTerms)
    ax.set_yticklabels(keyTerms)
    
    # Align ticks
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")
    
    # Annotate labels
    for i in range(numTerms):
        for j in range(numTerms):
            text = ax.text(j, i, coMatrix[i, j],
                       ha="center", va="center", color="b")

    ax.set_title("Co-occurence of Keywords")
    fig.tight_layout()
    #plt.show()
    figure = mpl_to_plotly(fig)  #fix this
    
    return figure # CHECK THIS RETURN 
'''
def heatmap_creator_2(keyTerms, coMatrix):
    #coMatrix = [[0,1,2], [0,3,2], [0,3,2]] - Hardcoded for debugging
    #keyTerms = ['hydrophobic', 'macromolecules', 'nucleosides'] - Hardcoded for debugging
    fig = ff.create_annotated_heatmap(coMatrix, x=keyTerms, y=keyTerms, colorscale='Viridis')
    return fig

@app.callback(
    Output('textarea-state-example-output', 'children'),
    [Input('textarea-state-example-button', 'n_clicks')],
    [State('textarea-state-example', 'value')])
def update_output(n_clicks, value): 
    if n_clicks > 0:
        keywords = list(value.split(","))
        return 'You have entered the following list of keywords: \n{}'.format(keywords)


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output_2(list_of_contents, list_of_names):
    return 'You have uploaded: \n' + str(list_of_names)


# Returns bar graph if upload files
@app.callback([Output('errors-info', 'children'),
              Output('graph', 'figure')],
              [Input('textarea-state-example-button', 'n_clicks'),
              Input('upload-data', 'contents')],
              [State('textarea-state-example', 'value'),
              State('upload-data', 'filename')])
def update_output_4(n_clicks, list_of_contents, value, list_of_names):
    children = ""
    figure = go.Figure()
    #n_clicks = 1
    if n_clicks > 0:
        # Turn the keywords entry box into a list
        keywords = list(value.split(","))
        numTerms = len(keywords)
        for i in range(numTerms):
            keywords[i] = keywords[i].lower()
        #print(keywords) #Debugging
        # Parse through PDFs and make list of strings
        if list_of_contents is not None:
            pdfList = []
            errors_list = []
            #for c, n in zip(list_of_contents, list_of_names):
                #parsed = parse_contents(c, n)
            for i in range(len(list_of_contents)):
                parsed = parse_contents(list_of_contents[i], list_of_names[i])
                #print(parsed) #Debugging
                if 'error' in parsed: 
                    errors_list.append(str(list_of_names[i]))
                else:
                    pdfList.append(parsed)
                    #print('{}').format(parsed)
            # Document errors
            if not errors_list:
                print('no errors')
                children = 'There were no errors reading in your uploaded documents.'
            else:
                errors_string = ''
                for i in errors_list:
                    errors_string = errors_string + i + ' ,'
                children = ('There were errors reading in the following uploaded documents: ' + errors_string)

            #Create numerical cooccurence matrix 
            
            coMatrix = [[0 for x in range(numTerms)] for y in range(numTerms)]
            print('matrix init')
            coMatrix = coOccMatrix(numTerms, keywords, pdfList)
            print('matrix creat')
            coMatrix = np.array(coMatrix)
            print(coMatrix)

            figure = heatmap_creator_2(keywords, coMatrix)
            #figure = go.Figure(data=go.Heatmap(
            #        z=coMatrix))

            #figure.show()
        else:
            children = 'You have not uploaded any documents yet.'
            figure = go.Figure()
    else:
        children = 'You have not entered any keywords yet.'
        figure = go.Figure()
            
    return children, figure 


if __name__ == '__main__':
    app.run_server(debug=True)
