from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
import json

def login_page(request):
    """登录页面"""
    return render(request, 'users/login.html')

@csrf_exempt
@api_view(['POST'])
def user_login(request):
    """用户登录API"""
    try:
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response({'success': False, 'error': '用户名和密码不能为空'}, status=400)

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'success': True,
                'message': '登录成功',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        else:
            return Response({'success': False, 'error': '用户名或密码错误'}, status=401)

    except Exception as e:
        return Response({'success': False, 'error': f'登录失败：{str(e)}'}, status=500)

@csrf_exempt
@api_view(['POST'])
def user_register(request):
    """用户注册API"""
    try:
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')

        if not username or not password:
            return Response({'success': False, 'error': '用户名和密码不能为空'}, status=400)

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'error': '用户名已存在'}, status=400)

        # 创建用户
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)

        return Response({
            'success': True,
            'message': '注册成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })

    except Exception as e:
        return Response({'success': False, 'error': f'注册失败：{str(e)}'}, status=500)

@api_view(['POST'])
def user_logout(request):
    """用户登出API"""
    logout(request)
    return Response({'success': True, 'message': '已退出登录'})

@api_view(['GET'])
def get_current_user(request):
    """获取当前用户信息"""
    if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
        return Response({
            'success': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_authenticated': True
            }
        })
    else:
        return Response({
            'success': True,
            'user': {
                'id': 0,
                'username': '游客',
                'is_authenticated': False
            }
        })

@api_view(['POST'])
def set_guest_mode(request):
    """设置游客模式"""
    request.session['guest_mode'] = True
    return Response({
        'success': True,
        'message': '已进入游客模式',
        'user': {
            'id': 1,  # 游客使用默认ID 1
            'username': '游客',
            'is_authenticated': False,
            'is_guest': True
        }
    })

def get_user_id(request):
    """获取用户ID，未登录返回0"""
    if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
        return request.user.id
    return 0
