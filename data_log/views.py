import json

from django.core.mail import mail_admins
from django.db.models.aggregates import Sum
from django.http import Http404
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.utils.text import slugify

from rest_framework import viewsets, permissions, versioning, exceptions, parsers
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from bestiary.models.items import GameItem
from herders.models import Summoner
from .game_commands import active_log_commands, accepted_api_params
from .models import FullLog, MagicShopRefreshReport, MagicBoxCraftingReport, WishReport, SummonReport, MagicBoxCraft, RuneCraftingReport, CraftRuneLog
from .util import transform_to_dict


class InvalidLogException(exceptions.APIException):
    # An API exception class that formats response into a {'message': xxx, 'reinit': true/false } shape
    status_code = 400
    default_detail = 'Invalid Log Data'
    default_code = 'invalid_log_data'

    def __init__(self, detail=None, code=None, reinit=True):
        message = detail if detail is not None else self.default_detail
        self.code = code if code is not None else self.default_code
        self.detail = {
            'detail': exceptions.ErrorDetail(message, self.default_code),
            'reinit': reinit,
        }


class LogData(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny, )
    versioning_class = versioning.QueryParameterVersioning  # Ignore default of namespaced based versioning and use default version defined in settings
    parser_classes = (parsers.JSONParser, parsers.FormParser)

    def list(self, request):
        return Response(accepted_api_params)

    def create(self, request):
        log_data = request.data.get('data')

        if request.content_type == 'application/x-www-form-urlencoded':
            # log_data will be a string, needs to be parsed as json
            log_data = json.loads(log_data)

        try:
            api_command = log_data['request']['command']
            wizard_id = log_data['request']['wizard_id']
        except (KeyError, TypeError):
            raise InvalidLogException(detail='Invalid log data format')

        if api_command not in active_log_commands:
            raise InvalidLogException('Unsupported game command')

        # Determine the user account providing this log
        if request.user.is_authenticated and wizard_id == request.user.summoner.com2us_id:
            summoner = request.user.summoner
        else:
            # Attempt to get summoner instance from wizard_id in log data
            summoner = Summoner.objects.filter(com2us_id=wizard_id).first()

        # Validate log data format
        if not active_log_commands[api_command].validate(log_data):
            FullLog.parse(summoner, log_data)
            raise InvalidLogException(detail='Log data failed validation')

        # Parse the log
        try:
            active_log_commands[api_command].parse(summoner, log_data)
        except Exception as e:
            mail_admins('Log server error', f'Request body:\n\n{log_data}')
            raise e

        response = {'detail': 'Log OK'}

        # Check if accepted API params version matches the active version
        if log_data.get('__version') != accepted_api_params['__version']:
            response['reinit'] = True

        return Response(response)


class AcceptedCommands(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny, )
    versioning_class = versioning.QueryParameterVersioning  # Ignore default of namespaced based versioning and use default version defined in settings
    renderer_classes = (JSONRenderer, )

    def list(self, request):
        return Response(accepted_api_params)


def _get_dashboard_report(model, field):
    if not hasattr(model, field):
        raise ValueError(f"Model {model} doesn't have {field} field.")
    
    qs_ids = []
    attr_list = []

    for report in model.objects.order_by('-generated_on').iterator(chunk_size=10):
        attr = getattr(report, field)
        if attr in attr_list:
            break
        attr_list.append(attr)
        qs_ids.append(report.pk)

    qs = model.objects.filter(pk__in=qs_ids)
    return qs, qs.first()


def data_reports(request):
    try:
        shop_refresh = MagicShopRefreshReport.objects.values('generated_on', 'log_count', 'unique_contributors').latest()
    except MagicShopRefreshReport.DoesNotExist:
        shop_refresh = None

    qs_magic_box, first_magic_box = _get_dashboard_report(MagicBoxCraftingReport, 'box_type')

    try:
        wish = WishReport.objects.values('generated_on', 'log_count', 'unique_contributors').latest()
    except WishReport.DoesNotExist:
        wish = None

    qs_summon, first_summon = _get_dashboard_report(SummonReport, 'item')
    qs_rune_crafting, first_rune_crafting = _get_dashboard_report(RuneCraftingReport, 'craft_level')

    content = {
        'view': 'data_reports',
        'reports': {
            'shop_refresh': shop_refresh,
            'magic_box': {
                'log_count': sum(rec.log_count for rec in qs_magic_box),
                'generated_on': first_magic_box.generated_on,
            } if first_magic_box else None,
            'wish': wish,
            'summon': {
                'log_count': sum(rec.log_count for rec in qs_summon),
                'generated_on': first_summon.generated_on,
            } if first_summon else None,
            'rune_crafting': {
                'log_count': sum(rec.log_count for rec in qs_rune_crafting),
                'generated_on': first_rune_crafting.generated_on,
            } if first_rune_crafting else None,
        }
    }

    return render(request, 'data_log/reports/base.html', content)


def _get_single_report(model, subview, **kwargs):
    filters = kwargs.get('filters', {})
    view = kwargs.get('view', 'data_reports')
    if filters:
        qs = model.objects.filter(**filters)
    else:
        qs = None

    try:
        if qs:
            content = model_to_dict(qs.latest())
        else:
            content = model_to_dict(model.objects.latest())
    except model.DoesNotExist:
        content = {'log_count': 0}
    
    content['view'] = view
    content['subview'] = subview

    return content


def data_report_magic_shop_refresh(request):
    content = _get_single_report(MagicShopRefreshReport, 'magic_shop')
    return render(request, 'data_log/reports/magic_shop.html', content)


def data_report_magic_box_crafting(request):
    qs_ids = []
    boxes = []
    for box_id, box_name in MagicBoxCraft.BOX_CHOICES:
        try:
            qs_ids.append(MagicBoxCraftingReport.objects.filter(box_type=box_id).latest().pk)
            boxes.append({
                'name': box_name,
                'slug': slugify(f"{box_id}-{box_name}"),
            })
        except MagicBoxCraftingReport.DoesNotExist:
            # no report for given box type
            continue
    
    qs = MagicBoxCraftingReport.objects.filter(pk__in=qs_ids)

    data = transform_to_dict(
        list(qs.values('box_type').annotate(count=Sum('log_count')).order_by('-count')),
        name_key='box_type',
    )

    # replace IDs with Names from Tuple
    for box_id, box_name in MagicBoxCraft.BOX_CHOICES:
        if box_id in data.keys():
            data[box_name] = data.pop(box_id)

    dashboard_data = {
        'boxes_crafted': {
            'type': 'occurrences',
            'total': sum(qs.values_list('log_count', flat=True)),
            'data': data,
        }
    }

    content = {
        'dashboard': dashboard_data,
        'box_list': boxes,
        'view': 'data_reports',
        'subview': 'magic_box',
    }

    return render(request, 'data_log/reports/magic_box.html', content)


def data_report_magic_box_crafting_detail(request, slug):
    filters = {
        'box_type': slug.split('-')[0],
    }
    content = _get_single_report(MagicBoxCraftingReport, 'magic_box', filters=filters)

    return render(request, 'data_log/reports/magic_box_detail.html', content)


def data_report_wish(request):
    content = _get_single_report(WishReport, 'wish')
    return render(request, 'data_log/reports/wish.html', content)


def data_report_summon(request):
    item_list = []
    qs_ids = []

    # get newest reports per item, iterator to not download all SummonReports
    for report in SummonReport.objects.order_by('-generated_on').iterator(chunk_size=10):
        if report.item in item_list:
            break
        item_list.append(report.item)
        qs_ids.append(report.pk)

    qs = SummonReport.objects.filter(pk__in=qs_ids)
    dashboard_data = {
        'summons_performed': {
            'type': 'occurrences',
            'total': sum(qs.values_list('log_count', flat=True)),
            'data': transform_to_dict(
                list(qs.values('item__name').annotate(count=Sum('log_count')).order_by('-count')),
                name_key='item__name',
            ),
        }
    }

    content = {
        'dashboard': dashboard_data,
        'item_list': item_list,
        'view': 'data_reports',
        'subview': 'summon',
    }

    return render(request, 'data_log/reports/summon.html', content)


def data_report_summon_detail(request, slug):
    try:
        item = GameItem.objects.get(slug=slug)
    except GameItem.DoesNotExist:
        raise Http404()

    filters = {
        'item': item,
    }
    content = _get_single_report(SummonReport, 'summon', filters=filters)
    content['item'] = item

    return render(request, 'data_log/reports/summon_detail.html', content)


def data_report_rune_crafting(request):
    qs_ids = []
    crafts = []
    for craft_id, craft_name in CraftRuneLog.CRAFT_CHOICES:
        try:
            qs_ids.append(RuneCraftingReport.objects.filter(craft_level=craft_id).latest().pk)
            crafts.append({
                'name': craft_name,
                'slug': slugify(f"{craft_id}-{craft_name}"),
            })
        except RuneCraftingReport.DoesNotExist:
            # no report for given box type
            continue
    
    qs = RuneCraftingReport.objects.filter(pk__in=qs_ids)

    data = transform_to_dict(
        list(qs.values('craft_level').annotate(count=Sum('log_count')).order_by('-count')),
        name_key='craft_level',
    )

    # replace IDs with Names from Tuple
    for craft_id, craft_name in CraftRuneLog.CRAFT_CHOICES:
        if craft_id in data.keys():
            data[craft_name] = data.pop(craft_id)

    dashboard_data = {
        'runes_crafted': {
            'type': 'occurrences',
            'total': sum(qs.values_list('log_count', flat=True)),
            'data': data,
        }
    }

    content = {
        'dashboard': dashboard_data,
        'craft_list': crafts,
        'view': 'data_reports',
        'subview': 'rune_crafting',
    }

    return render(request, 'data_log/reports/rune_craft.html', content)


def data_report_rune_crafting_detail(request, slug):
    filters = {
        'craft_level': slug.split('-')[0],
    }
    content = _get_single_report(RuneCraftingReport, 'rune_crafting', filters=filters)

    print(content)

    return render(request, 'data_log/reports/rune_craft_detail.html', content)
# 