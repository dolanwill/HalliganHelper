from django.contrib.auth.models import User
from django.utils.html import escape, strip_tags
# from tastypie import fields
from tastypie.http import HttpBadRequest, HttpUnauthorized
import pytz
import logging
import datetime
from django.conf import settings
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from .authorization import NoEditAuthorization, RequestAuthorization
from .models import Course, TA, OfficeHour, Request
# from .models import Student
from HalliganAvailability.authentication import OAuth20Authentication
# from .tasks import cancel_hours
logger = logging.getLogger('api')


def _now():
    now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    return now


class CommonMeta(object):
    authorization = DjangoAuthorization()
    authentication = MultiAuthentication(OAuth20Authentication(),
                                         SessionAuthentication())
    limit = 0


class CourseResource(ModelResource):
    class Meta(CommonMeta):
        queryset = Course.objects.all()
        authorization = NoEditAuthorization()
        filtering = {
            'Name': ['exact', 'iexact', 'startswith', ],
            'Number': ['exact', 'lte', 'lt', 'gte', 'gt', ],
            'Professor': ['exact', 'iexact', 'startswith', ],
        }
        fields = ['Name', 'Number', 'Professor', 'students']
        allowed_methods = ['get']


class TAResource(ModelResource):
    class Meta(CommonMeta):
        authorization = NoEditAuthorization()
        queryset = TA.objects.active()
        # queryset = TA.objects.all()
        fields = ['headshot', 'active']
        allowed_methods = ['get']

    def get_object_list(self, request):
        if 'get_all' in request.GET:
            return TA.objects.all()
        else:
            return TA.objects.active()

    def dehydrate(self, bundle):
        bundle.data['full_name'] = bundle.obj.usr.get_full_name()
        return bundle


class OfficeHourResource(ModelResource):
    class Meta:
        queryset = OfficeHour.objects.all()


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()


class RequestResource(ModelResource):
    class Meta(CommonMeta):
        queryset = Request.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch']
        authorization = RequestAuthorization()

    def _can_student_update(self, user, new_keys, item_id):
        student_allowed_updates = set(['whereLocated',
                                       'question',
                                       'cancelled'])
        item_to_update = Request.objects.get(pk=item_id)

        is_owner = item_to_update.student.usr.pk == user.pk

        changes_allowed = new_keys.issubset(student_allowed_updates)
        # print ("OWNER? {}".format(is_owner))
        # print ("CHANGES ALLOWED? {}".format(changes_allowed))

        if (not is_owner) or (is_owner and not changes_allowed):
            print ("RETURN FALSE: OWNER IS {} AND CHANGES ALLOWED IS {}" \
                   .format(is_owner, changes_allowed))

            return False

        return True

    def _can_ta_update(self, user, new_keys):
        ta_allowed_updates = set(['solved', 'checked_out'])

        try:
            is_ta = user.ta.active
        except TA.DoesNotExist:
            is_ta = False

        changes_allowed = new_keys.issubset(ta_allowed_updates)
        if (not is_ta) or (is_ta and not changes_allowed):
            return False

        return True

    # def obj_update(self, bundle, **kwargs):
    #     if bundle.data['solved'] and bundle.data['whenSolved'] is None:
    #         #TODO: Actual do things
    #         pass
    #         # bundle.data['whenAsked'] = _now()
    #         # bundle.data['who_solved'] = bundle.request.user.ta
    #     return super(RequestResource, self).obj_update(bundle, **kwargs)

    def patch_detail(self, request, **kwargs):
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('CONTENT_TYPE',
                                                        'application/json'))
        new_keys = set(data.keys())

        student_update = self._can_student_update(request.user, new_keys,
                                                  kwargs['pk'])
        ta_update = self._can_ta_update(request.user, new_keys)

        if (not student_update) and (not ta_update):
            print( "STUDENT: {}".format(student_update))
            print( "TA: {}".format(ta_update))
            return HttpUnauthorized("You are not authorized")
        print(request.body)
        try:
            ret_val = super(RequestResource, self).patch_detail(request, **kwargs)
        except Exception:
            print "RAISING A THING"
        return ret_val
