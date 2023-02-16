from django.http import HttpResponseNotFound
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from .decorators import get_account


class ModelViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        # If this method is in the removed methods list, return 404.
        if 'list' in self.removed_methods:
            return HttpResponseNotFound()

        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.queryset_filter(queryset, request.GET)
        if self.pagination_class:
            queryset = self.pagination_class().paginate_queryset(queryset, request)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        # If this method is in the removed methods list, return 404.
        if 'create' in self.removed_methods:
            return HttpResponseNotFound()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'status': 'success', 'data': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        # If this method is in the removed methods list, return 404.
        if 'retrieve' in self.removed_methods:
            return HttpResponseNotFound()

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'status': 'success', 'data': serializer.data})

    def update(self, request, *args, **kwargs):
        # If this method is in the removed methods list, return 404.
        if 'update' in self.removed_methods:
            return HttpResponseNotFound()

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'status': 'success', 'data': serializer.data})

    def partial_update(self, request, *args, **kwargs):
        # If this method is in the removed methods list, return 404.
        if 'partial_update' in self.removed_methods:
            return HttpResponseNotFound()

        return self.update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        # If this method is in the removed methods list, return 404.
        if 'destroy' in self.removed_methods:
            return HttpResponseNotFound()

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'status': 'success', 'data': {}})

    def queryset_filter(self, queryset, request_get, Or=False):
        var_beyond = {
            'queryset': queryset,
        }

        if Or:
            # OR filter
            in_command = f'var_beyond["queryset"] = var_beyond["queryset"].filter('
            for item in request_get.items():
                if item[0].find('_') != -1:
                    key = item[0]
                else:
                    key = item[0] + '__icontains'
                value = item[1]

                if item[1].isdigit():
                    in_command += f' Q({key}={value}) |'
                else:
                    in_command += f' Q({key}="{value}") |'
            in_command = in_command[:-1] + ')'
            try:
                exec(in_command)
            except:
                pass
        else:
            # AND filter
            for item in request_get.items():
                if item[0].find('_') != -1:
                    key = item[0]
                else:
                    key = item[0] + '__icontains'
                value = item[1]
                if item[1].isdigit():
                    in_command = f'var_beyond["queryset"] = var_beyond["queryset"].filter({key}={value})'
                else:
                    in_command = f'var_beyond["queryset"] = var_beyond["queryset"].filter({key}="{value}")'

                try:
                    exec(in_command)
                except:
                    pass

        return var_beyond['queryset']


class DisabledCRUDMixin(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        return HttpResponseNotFound()

    def create(self, request, *args, **kwargs):
        return HttpResponseNotFound()

    def retrieve(self, request, *args, **kwargs):
        return HttpResponseNotFound()

    def update(self, request, *args, **kwargs):
        return HttpResponseNotFound()

    def partial_update(self, request, *args, **kwargs):
        return HttpResponseNotFound()

    def destroy(self, request, *args, **kwargs):
        return HttpResponseNotFound()
