#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains Helper functions for Web Spider."""


def combine_uri(part_one, part_two):
    """Method that deals with combining URLs."""
    if not part_one.endswith('/'):
        part_one += '/'
    if part_two.startswith('/'):
        part_two = part_two[1:]

    return part_one + part_two


def finalise_url(raw_url, netloc, scheme):
    """Method that finalises URL."""
    url = raw_url

    if raw_url[:4] != 'http' and raw_url[:2] != '//':
        url = combine_uri(scheme + '://' + netloc, raw_url)
    elif raw_url[:2] == '//':
        url = scheme + ':' + raw_url
    elif raw_url[:1] == '/' and  raw_url[1] != '/':
        url = scheme + ':' + netloc + raw_url

    return url


def finalise_email(email):
    """Method that finalises email and also applies common fixes."""
    # Convert email address to lowercase.
    email = email.lower()

    # Remove any leading or trailing dot.
    email = email.strip('.')

    # Remove pre-filled fields from email string.
    if email.find('?') > -1:
        position = email.find('?')
        email = email[:position]

    # Fix for common tricks that people are using.
    email = email.replace(' dot ', '.')
    email = email.replace(' at ', '@')

    return email