from django.db import models
from django.contrib.auth.models import User

class UserProfilePic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    pic = models.FileField(null=True)



class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    jwt = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.user.username


class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200, null=True)
    detail = models.TextField(null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username + "  " + self.title



class Likes(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, related_name="visitor_like", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.username + "  " + self.blog.title


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, related_name="visitor_coment", on_delete=models.CASCADE, null=True)
    msg = models.TextField(null=True)

    def __str__(self):
        return self.user.username + "  " + self.blog.title + "  " + self.msg



