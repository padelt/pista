#!/usr/bin/env python

from peewee import *
from owntracks import cf
import datetime
import os
import sys

db = None
if cf.dbengine == 'postgresql':
    # Use PostreSQL configuration
    db = PostgresqlDatabase(cf.dbname,
        user=cf.dbuser,
        port=cf.dbport,
        threadlocals=True)
else:
    db = MySQLDatabase(cf.dbname,
        user=cf.dbuser,
        passwd=cf.dbpasswd,
        host=cf.dbhost,
        port=cf.dbport,
        threadlocals=True)


class OwntracksModel(Model):

    class Meta:
        database = db

class Geo(OwntracksModel):
    ghash           = CharField(null=False, max_length=6, unique=True)
    src             = IntegerField(null=True)       # source of reverse geo
    cc              = CharField(null=True, max_length=2)
    addr            = CharField(null=False)

class Location(OwntracksModel):
    topic           = BlobField(null=False)
    tid             = CharField(null=False, max_length=2)
    lat             = DecimalField(null=False, max_digits=10, decimal_places=7)
    lon             = DecimalField(null=False, max_digits=10, decimal_places=7)
    tst             = DateTimeField(default=datetime.datetime.now, index=True)
    # acc             = DecimalField(null=True, max_digits=6, decimal_places=1)
    # batt            = DecimalField(null=True, max_digits=3, decimal_places=1)
    # waypoint        = TextField(null=True)  # desc in JSON, but desc is reserved SQL word
    # event           = CharField(null=True)
    vel             = IntegerField(null=True)
    alt             = IntegerField(null=True)
    cog             = IntegerField(null=True)
    trip            = IntegerField(null=True)
    dist            = IntegerField(null=True)
    t               = CharField(null=True, max_length=1)
    ghash           = CharField(null=True, max_length=6)
    cc              = CharField(null=True, max_length=2)

    class Meta:
        indexes = (
            # Create non-unique on tid
            (('tid', ), False),
            # (('topic', ), False),  # create index l_topic on location(topic (100));
        )

class RAWdata(OwntracksModel):
    topic           = BlobField(null=False)
    tst             = DateTimeField(default=datetime.datetime.now, index=True)
    payload         = TextField(null=True)

# Optional: operators. Useful for Greenwich only
class Operators(OwntracksModel):
    topic           = BlobField(null=False)
    tst             = DateTimeField(default=datetime.datetime.now, index=True)
    plmn            = CharField(null=True, max_length=8)
    extended        = CharField(null=True)

class Waypoint(OwntracksModel):
    topic           = BlobField(null=False)
    username        = CharField(null=False)
    device          = CharField(null=False)
    tid             = CharField(null=False, max_length=2)
    lat             = DecimalField(null=False, max_digits=10, decimal_places=7)
    lon             = DecimalField(null=False, max_digits=10, decimal_places=7)
    tst             = DateTimeField(default=datetime.datetime.now)
    rad             = IntegerField(null=True)
    waypoint        = CharField(null=True)

    class Meta:
        indexes = (
            # Create a unique index on tst
            (('tst', ), True),
        )


class User(OwntracksModel):
    username        = CharField(null=False, unique=True)
    pwhash          = CharField(null=False)
    superuser       = IntegerField(null=False)
    org             = IntegerField(null=True)
    token           = CharField(null=True)
    note            = CharField(null=True)
    tstamp          = DateTimeField(default=datetime.datetime.now)


class Acl(OwntracksModel):
    username        = CharField(null=False)
    topic           = CharField(null=False)
    rw              = IntegerField(null=False)
    note            = CharField(null=True)
    tstamp          = DateTimeField(default=datetime.datetime.now)

    class Meta:
        indexes = (
            # Create unique on username, topic
            (('username', 'topic'), True),
        )

class Params(OwntracksModel):
    name            = CharField(null=True)
    host            = CharField(null=True)
    port            = IntegerField(null=True)
    tls             = IntegerField(null=True)
    auth            = IntegerField(null=True)
    mqttuser        = CharField(null=True)
    mqttpass        = CharField(null=True)
    certurl         = CharField(null=True)
    trackurl        = CharField(null=True)


class Inventory(OwntracksModel):
    imei            = CharField(null=False, max_length=15, unique=True)
    tid             = CharField(null=True, max_length=2)
    version         = CharField(null=True, max_length=10)
    startup         = IntegerField(null=True)   # epoch
    label           = CharField(null=True)
    tstamp          = DateTimeField(default=datetime.datetime.now)

    class Meta:
        indexes = (
        )


if __name__ == '__main__':
    db.connect()

    if cf.g('features', 'plmn', False) == True:
        try:
            Operators.create_table(fail_silently=True)
        except Exception, e:
            print str(e)

    try:
        Location.create_table(fail_silently=True)
    except Exception, e:
        print str(e)

    try:
        Waypoint.create_table(fail_silently=True)
    except Exception, e:
        print str(e)

    try:
        Geo.create_table(fail_silently=True)
    except Exception, e:
        print str(e)

    if cf.g('features', 'rawdata', False) == True:
        try:
            RAWdata.create_table(fail_silently=True)
        except Exception, e:
            print str(e)

    try:
        User.create_table(fail_silently=True)
    except Exception, e:
        print str(e)

    try:
        Acl.create_table(fail_silently=True)
    except Exception, e:
        print str(e)

    try:
        Inventory.create_table(fail_silently=True)
    except Exception, e:
        print str(e)

    try:
        Params.create_table(fail_silently=True)
    except Exception, e:
        print str(e)