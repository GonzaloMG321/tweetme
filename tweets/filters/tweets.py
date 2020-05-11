"""Tweets filter"""
# Filter
from django_filters.rest_framework import FilterSet
import django_filters
# Models
from tweets.models import Tweet

class TweetFilter(FilterSet):
    content = django_filters.CharFilter(field_name='content', lookup_expr='contains')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='exact')
    class Meta:
        model = Tweet
        fields = []