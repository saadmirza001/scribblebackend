from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import jwt
from Blog.models import *
from django.conf import settings
from backend.tasks import SendMailTask
from django.shortcuts import render


import requests
import json

headers = { "X-Api-Key": "test_310f45ea5b1f1b84a730042e2d9",
            "X-Auth-Token": "test_b11cc750115375b7ead968f3811"
            }


@api_view(http_method_names=["GET", "POST"])
def SignUp(request):
    if request.method == "POST":
        data = request.data

        #### verify your Username....
        username = data['username']
        user = User.objects.filter(username=username)
        if user:
            return Response(data = {
                'Error':'This User Already Exist......'
            })

        user = User.objects.create_user(username=username, email=data['email'],
                                        password=data['pass'])
        user.first_name = data['name']
        user.last_name = data["mobile"]
        user.save()

        ## store image...
        pic = request.FILES["profile"]
        UserProfilePic.objects.create(pic=pic, user = user)

        user = User.objects.filter(username = username).values().first()
        user.pop('password')
        return Response(data={
            "data":user
        })
    return Response(data={
        "Status": "Get Request not Allowed.."
    })

import datetime
def GenerateToken_and_SetCookie(user):
    response = Response()
    user_auth_token = {
        'username':user.username,
        'exp':datetime.datetime.now() + datetime.timedelta(days=5),
        'iat':datetime.datetime.now()
    }
    token = jwt.encode(user_auth_token, settings.SECRET_KEY, algorithm='HS256')
    user = User.objects.get(username=user.username)
    data, status = Token.objects.get_or_create(user=user)
    data.jwt = token
    data.save()
    response.set_cookie(key="token_auth", value=token, httponly=True)
    response.data = {"Token":token}
    return response




@api_view(http_method_names=["GET", "POST"])
def Login(request):
    if request.method == "POST":
        username = request.data["username"]
        password = request.data["pass"]
        user = authenticate(username = username, password = password)
        if user:
            login(request, user)
            response = GenerateToken_and_SetCookie(user)
            response.data["Status"] = "LoggedIn"
            response.data['Username'] = user.username
            response.data['Name'] = user.first_name
            response.data['Email'] = user.email
            response.data["profileUrl"] = ""

            pic = UserProfilePic.objects.filter(user= user).first()
            if pic:
                response.data["profileUrl"] = pic.pic.url

            return response

        return Response(data={
            "Error":'Username or Password is Incorrect....'
        })



@api_view(http_method_names=["GET"])
def CountData(request, username):
    user = User.objects.get(username=username)
    all_blogs = Blog.objects.filter(user=user)

    blogsCount = len(all_blogs)
    likes = 0
    comments = 0
    for blog in all_blogs:
        like = Likes.objects.filter(blog=blog)
        comment = Comment.objects.filter(blog=blog)

        likes += len(like)
        comments += len(comment)

    all_other_blogs = []
    Blogs = Blog.objects.all()
    for blog in Blogs:
        isLikedbyCurrentUser = Likes.objects.filter(blog=blog, user=user).first()
        if blog.user.username != user.username:
            blogsDict = Blog.objects.filter(id = blog.id).values().first()
            blogsDict['user_id'] = blog.user.first_name

            blogsDict['likes'] = len(Likes.objects.filter(blog = blog))
            blogsDict['commects'] = Comment.objects.filter(blog = blog).values()
            blogsDict['isLiked'] = False
            if isLikedbyCurrentUser:
                blogsDict['isLiked'] = True

            all_other_blogs.append(blogsDict)


    return Response(data={
        "blogs":blogsCount, "likes":likes, "comments":comments, 'all_blogs':all_blogs.values(),
        "all_other_blogs":all_other_blogs
    })



@api_view(http_method_names=["POST"])
def WriteBlog(request):
    if request.method == "POST":
        data = request.data
        title = data['title']
        detail = data['blog']
        user = data['user']
        user = User.objects.filter(username=user).first()
        if user:
            Blog.objects.create(user=user, title=title, detail=detail)
            return Response(data= {
                "Status":'Created'
            })
        else:
            return Response(data={
                "Status": 'Error',
                "Error":'User not Found..'
            })

from django.core.mail import send_mail
from django.template.loader import get_template


def SendMail(email, receiverName,likedUser, blogTitle):
    today = date.today()
    from_email = settings.EMAIL_HOST_USER
    to_mail = [email]
    msg = ""
    sub = "Liked Mail.."
    html = get_template("liked_mail.html").render({"receiverName":receiverName,
                                                   "likedUser":likedUser,
                                                   "blogTitle":blogTitle, "date":today})

    send_mail(sub, msg, from_email, to_mail, html_message=html ,fail_silently=True)



# import urllib.parse
# import urllib.request
# def SendMsg(number, receiverName,likedUser, blogTitle):
#     apiKey = "232419AT2rwRRUo5b77e616"
#     msg = f"Hi {receiverName} !\n {likedUser} has liked your blog. \n Title:  {blogTitle} \n Thanks..\n TechSim+ Team."
#     sender = "TCHSIM"
#     route = "4"
#     url = "http://api.msg91.com/api/sendhttp.php"
#
#     values = {
#         "authkey":apiKey, "mobiles":number, "message":msg, "sender":sender, "route":route
#     }
#
#     data = urllib.parse.urlencode(values)
#     data = data.encode("ascii")
#     req = urllib.request.Request(url, data)
#     res = urllib.request.urlopen(req)
#     print("Its Done....")



@api_view(http_method_names=["GET"])
def LikeBlogbyUser(request, username,blogId):
    user = User.objects.filter(username=username).first()
    blog = Blog.objects.filter(id = blogId).first()
    like = Likes.objects.filter(user=user, blog=blog)
    if not like:
        Likes.objects.create(user=user, blog=blog)
        print("We are Sending the MAIL...")
        SendMailTask.delay(blog.user.email, blog.user.first_name, user.first_name, blog.title)
        # if blog.user.last_name:
        #     print("Sending the msg...")
        #     SendMsg(blog.user.last_name, blog.user.first_name, user.first_name, blog.title)
        # SendMailTask.delay(blog.user.email,blog.user.first_name, user.first_name, blog.title )

        return Response(data={
            "Status": True
        })

    else:
        like.delete()
        return Response(data={
            "Status": False
        })


@api_view(http_method_names=["POST"])
def WriteComment(request, username, blogId):
    if request.method == "POST":
        data = request.data
        comment = data["comment"]
        user = User.objects.get(username=username)
        blog = Blog.objects.get(id = blogId)
        Comment.objects.create(blog=blog, user=user, msg=comment)
        return Response(data = {
            "Status":"Done..."
        })


@api_view(http_method_names=["GET", "POST"])
def SendPaymentRequest(request, username):
    user = User.objects.get(username=username)
    donorName = user.first_name
    payloads = {
        "purpose": 'Donate Amount..',
        'amount': '10',
        "buyer_name" : donorName,
        "email" : 'scribbleblogs@gmail.com',
        "phone": "7675074823",
        "redirect_url":"http://127.0.0.1:3000/paycheck",
        'send_email':True,
        'send_sms':True
    }

    response = requests.post("https://test.instamojo.com/api/1.1/payment-requests/", data=payloads, headers=headers)
    textResponse = response.text
    jsonResponse = json.loads(textResponse)
    print(jsonResponse)
    paymentUrl = jsonResponse["payment_request"]["longurl"]
    return Response (data = {
        "payUrl" : paymentUrl
    })


#pip install celery
#pip install redis
#pip3 install django-celery-beat
#pip3 install django-celery-results

def Home(request):
    return render(request, "index.html")
