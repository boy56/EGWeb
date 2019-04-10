# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from EGWeb.dataservice import search_event_by_theme, search_trigger_by_name, search_trigger_by_theme


def chouqu(request):
    return render(request, 'Chouqu.html')

def tupu(request):
    return render(request, 'Tupu.html')

def common(request):
    return render(request, 'Common.html')


# 某些情况下django中间件会进行保护, 阻挡post请求从而出现403错误
@csrf_exempt    #关闭csrf保护功能
def search(request):
    
    search_type = request.GET['type']
    search_content = request.GET['content']
    if search_type == 'E':
        result = search_event_by_theme(search_content)
        if result['status'] == 0:
            result['answer'] = "没有找到相关信息"
        else:
            result['answer'] = "关于\"" + search_content + "\"的事件信息"
    elif search_type == 'T':
        result = search_trigger_by_name(search_content)
        if result['status'] == 0:
            result['answer'] = "没有找到相关信息"
        else:
            result['answer'] = "关于\"" + search_content + "\"的触发词信息"
    elif search_type == 'ET':
        result = search_trigger_by_theme(search_content)
        if result['status'] == 0:
            result['answer'] = "没有找到相关信息"
        else:
            result['answer'] = "关于\"" + search_content + "\"事件的触发词信息"
    else:
        result['status'] = 0
        result['answer'] = "没有找到相关信息"
        result['nodes'] = []
        result['edges'] = []

    return JsonResponse(result)

def find_common_pattern(request):
    result = {}
    return JsonResponse(result)


