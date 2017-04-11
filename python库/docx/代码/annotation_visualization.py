#coding=utf-8

from docx import Document
from docx.shared import RGBColor
import json


def load_question(question_path):
    'TODO: load question from local file.'
    que = []
    with open(question_path, 'r') as question_file:
        for question in question_file:
            que.append(question.rstrip('\n'))
    return que

global color
color=[RGBColor(255,0,0),RGBColor(34,139,34),RGBColor(238,201,0),RGBColor(160,32,240)]

def add_doc(question_list,color_id):
    for i,ch in enumerate(question_list):
        run = p.add_run(ch)
        run.font.color.rgb = color[color_id[i]]

document = Document()

document.add_heading('annotation',0)

questions = load_question('data/base_questions_v1.6/questions_20170324.csv')

with open('data/base_questions_v1.6/result/annotations.json') as annotations_list:
    annotations=[]
    for row in annotations_list:
        annotations.append(row.rstrip('\n'))

for i in range(len(annotations)):
    if annotations[i]=='':
        p = document.add_paragraph()
        run = p.add_run(str(i+1)+'. time out')
    elif annotations[i]=='null':
        p = document.add_paragraph()
        run = p.add_run(str(i+1)+'. null')
    else:
        annotation=json.loads(annotations[i]) #'annotation' is list
        #print annotation
        #print len(annotation)
        a=questions[i]
        question_list=[]
        color_id=[]
        p = document.add_paragraph()
        run = p.add_run(str(i+1)+'. ')
        for j in range(len(annotation)):#根据annotation返回的分割方式，建立question_list
            element=annotation[j]
            #print type(element)
            #print element
            if str(element[u'tokens']) == 'None':
                question_list.append(u'错误1')
                color_id.append(0)
            else:
                for m in range(len(element[u'tokens'])):
                    tokens=element[u'tokens'][m]
                    #print tokens
                    #print a[tokens[u'begin']:tokens[u'end']]
                    if len(element[u'tokens'])==1:
                        token_det = a[tokens[u'begin']:tokens[u'end']]
                    elif len(element[u'tokens'])>1:
                        if m!=len(element[u'tokens'])-1:
                            token_det = a[tokens[u'begin']:tokens[u'end']]+'-'
                        elif m==len(element[u'tokens'])-1:
                            token_det = a[tokens[u'begin']:tokens[u'end']]
                    question_list.append(token_det)
                    tokens_type=element[u'type']
                    if tokens_type == u'phrase':
                        color_id.append(1)
                    elif tokens_type == 'filter':
                        color_id.append(2)
                    else:
                        print 'gg'
                question_list.append('|')
                color_id.append(0)
        add_doc(question_list,color_id)

document.save('data/base_questions_v1.6/result/annotation_visualization.docx')
#保存文件
