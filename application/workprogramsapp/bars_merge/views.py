from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from workprogramsapp.bars_merge.bars_api_getter import get_educational_program_main, get_disciplines, \
    get_one_educational_program, get_list_of_regular_checkpoints, post_checkpoint_plan
from workprogramsapp.bars_merge.bars_function_for_threading import generate_single_checkpoint
from workprogramsapp.bars_merge.checkpoint_template import generate_checkpoint, get_checkpoints_type, \
    generate_discipline, generate_checkpoint_plan, generate_fos
from workprogramsapp.bars_merge.models import BarsEPAssociate, BarsWorkProgramsAssociate, HistoryOfSendingToBars
from workprogramsapp.bars_merge.serializers import BarsEPAssociateSerializer, BarsWorkProgramsAssociateSerializer, \
    HistoryOfSendingBarsSerializer
from workprogramsapp.models import WorkProgram, FieldOfStudy, ImplementationAcademicPlan, EvaluationTool, \
    DisciplineSection, WorkProgramChangeInDisciplineBlockModule, СertificationEvaluationTool, \
    WorkProgramIdStrUpForIsu


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def FindSimilarEP(request):
    # Достаем из АПИ БАРС 2.0 Все ОП
    ep = get_educational_program_main()
    list_of_new_bars_ep = []

    # Проходимся по полученным ОП
    for program in ep:
        # Если такой ОП нету в нашем сервисе, создаем новую
        if not BarsEPAssociate.objects.filter(bars_id=program["id"]):
            try:
                field_of_study = list(ImplementationAcademicPlan.objects.filter(
                    field_of_study__number=program["code"][:program["code"].rfind(".")]))
                new_bars_ep = BarsEPAssociate(bars_id=program["id"])
                new_bars_ep.save()
                new_bars_ep.base_field_of_study.add(*field_of_study)
                list_of_new_bars_ep.append(new_bars_ep)
            except FieldOfStudy.DoesNotExist:
                pass
    serializer = BarsEPAssociateSerializer(list_of_new_bars_ep, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def FindSimilarWP(request):
    # Достаем из АПИ БАРС 2.0 Все РПД
    wp = get_disciplines()
    wp_db = []
    for program in wp:
        if not BarsWorkProgramsAssociate.objects.filter(bars_id=program["id"]):
            wp_to_append = list(WorkProgram.objects.filter(title=program["name"]))
            if wp_to_append:
                wp_object = BarsWorkProgramsAssociate(bars_id=program["id"], term=program["term"])
                wp_object.save()
                wp_object.base_work_programs.add(*wp_to_append)
                wp_db.append(wp_object)
    serializer = BarsWorkProgramsAssociateSerializer(wp_db, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def CreateCheckPoint(request):
    # TODO: УБРАТЬ ХАРДКОДИНГ
    work_program_id = request.data.get('work_program_id')
    field_of_study_id = request.data.get('field_of_study_id')
    term = request.data.get('term')

    # Переменные для формирования запроса к БАРС
    point_distribution = 0
    bars_id = WorkProgram.objects.get(
        id=work_program_id).wp_isu_id
    types_checkpoints = get_list_of_regular_checkpoints()  # Список оценочных средств в БАРСе
    list_regular = []
    has_course_project = False
    course_project = None
    final_checkpoint = None
    discipline = None
    extra_points = True if WorkProgram.objects.get(id=work_program_id).extra_points else False
    field_of_study = FieldOfStudy.objects.get(id=field_of_study_id)

    # Получение дисцплины из направления
    wp_in_change = WorkProgramChangeInDisciplineBlockModule.objects.filter(work_program=work_program_id,
                                                                           discipline_block_module__descipline_block__academic_plan__field_of_study=field_of_study).distinct()
    wp_in_change = wp_in_change[0]

    """
    Пока названия имен в Конструкторе РПД не совпадают с именами в БАРСе этот код не имеет смысла, 
    заменяется тем что ниже
    
    educational_bars_id = WorkProgramInFieldOfStudy.objects.filter(
        work_program_change_in_discipline_block_module=wp_in_change)[0].id_str_up
    """

    # Поиск информции об образовательной программе в барсе, получение ее таблицы
    programs = []
    bars_education = get_one_educational_program(bars_id, term)
    for educ in bars_education:
        if educ["code"] == field_of_study.number + ".":
            programs = educ

    # Поиск относительного семестра из переданного абсолютного
    semesters = str(wp_in_change.credit_units).split(",")
    needed_semester = -1
    count = 1
    for i, el in enumerate(semesters):
        if int(el) > 0:
            if i + 1 == term:
                needed_semester = count
                break
            count += 1

    # Поиск оценочных средства для семетра, а также нахождение БАРСовских типов оценочных срелств
    evaluation_tools = EvaluationTool.objects.filter(evaluation_tools__in=DisciplineSection.objects.filter(
        work_program__id=work_program_id)).distinct().filter(semester=needed_semester)
    for eva in evaluation_tools:
        for el in types_checkpoints:
            if el["name"] == eva.type:
                id = el["id"]
        list_regular.append(
            generate_checkpoint(name=eva.name, min=eva.min, max=eva.max, week=int(eva.deadline), type_id=id,
                                key=eva.check_point))
    certificate = СertificationEvaluationTool.objects.filter(work_program=work_program_id, semester=needed_semester)
    for cerf in certificate:
        if int(cerf.type) == 4:
            has_course_project = True
            course_project = generate_checkpoint(name=cerf.name, min=cerf.min, max=cerf.max, week=None, type_id=id,
                                                 key=True)
        else:
            point_distribution = 100 - cerf.max
            final_checkpoint = generate_checkpoint(name=cerf.name, min=cerf.min, max=cerf.max, week=None,
                                                   type_id=get_checkpoints_type(int(cerf.type)), key=True)

    discipline = generate_discipline(bars_id=bars_id, name=WorkProgram.objects.get(id=work_program_id).title, term=term,
                                     course_project=has_course_project)
    checkpoint_plan = generate_checkpoint_plan(regular_checkpoint=list_regular, programs=programs,
                                               discipline=discipline,
                                               final_checkpoint=final_checkpoint,
                                               course_project_checkpoint=course_project,
                                               term=term, point_distribution=point_distribution,
                                               additional_points=extra_points,
                                               alternate_methods=False, has_course_project=has_course_project)
    return Response(checkpoint_plan)


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def SendCheckpointsForAcceptedWP(request):
    """
    Отправка всех прошедших экспертизу РПД, в БАРС
    Параметры:
    year : Поле вида 'YYYY/YYYY', указывает учебный год в который надо отправить РПД [str]
    send_semester : 1 - семетр осенний, 0 - семестр весенний [int]
    one_wp: необязательное поле, указывается id одной РПД для отправки в БАРС
    """
    year = request.data.get('year')
    send_semester = request.data.get('send_semester')
    one_wp = request.data.get('one_wp')
    setup_bars = (year, send_semester)  # Устанавливает корректную дату и семестр в барсе (аргумент для БАРС-функций)
    # небольшой костыль из-за некоторых ньюансов (цикл семестров начинается с 0)
    types_checkpoints = get_list_of_regular_checkpoints(setup_bars)  # получаем список типов чекпоинтов из БАРС
    if send_semester == 0:
        send_semester = 1
    else:
        send_semester = 0

    # Отсылаем ли мы одну дисципилну или же все с пометкой "отправить в барс"
    if not one_wp:
        needed_wp = WorkProgram.objects.filter(expertise_with_rpd__expertise_status__contains='AC',
                                               bars=True).distinct()
    else:
        needed_wp = WorkProgram.objects.filter(pk=one_wp)
    all_sends = []  # Список всего того что отправили в барс, нужен для респонса

    for work_program in needed_wp:  # для каждой РПД формируем отдельный запрос в БАРС
        relative_bool = True  # Длится ли дисциплина дольше чем один семестр
        count_relative = 1  # Счетчик относительных семестров

        # Проверка для булевой переменной, идет ли дисциплина в нескольких семестрах
        evaluation_tools = EvaluationTool.objects.filter(evaluation_tools__in=DisciplineSection.objects.filter(
            work_program__id=work_program.id))
        min_sem = 12
        max_sem = 1
        for eva in evaluation_tools:
            if eva.semester == None:
                break
            if eva.semester < min_sem:
                min_sem = eva.semester
            if eva.semester > max_sem:
                max_sem = eva.semester
        if max_sem != min_sem:
            relative_bool = False

        # Блок отвечающий за поиск оценочных средств в семестре
        for now_semester in range(0, 12):  # Цикл по семестрам
            imp_list = []  # Список всех учебных планов для этого семестра
            # Создание реуглярного выражения для того чтобы отфильтровать УП и инфу о РПД за этот семестр в цикле
            cred_regex = r""
            for i in range(12):
                if i == now_semester:
                    cred_regex += "[^0]\.[0-9],\s"
                else:
                    cred_regex += "(([0-9]\.[0-9])|[0]),\s"
            cred_regex = cred_regex[:-3]

            # Получаем все УП для данного семестра РПД (нужно для каунтера отнсительного семестра)
            implementation_of_academic_plan_all = ImplementationAcademicPlan.objects.filter(
                academic_plan__discipline_blocks_in_academic_plan__modules_in_discipline_block__change_blocks_of_work_programs_in_modules__work_program=work_program,
                academic_plan__discipline_blocks_in_academic_plan__modules_in_discipline_block__change_blocks_of_work_programs_in_modules__zuns_for_cb__zuns_for_wp__ze_v_sem__iregex=cred_regex).distinct()
            # Список УП с учетом актуального семестра отправки в БАРС
            implementation_of_academic_plan = implementation_of_academic_plan_all.filter(
                year=datetime.now().year - now_semester // 2)
            isu_wp_id = None
            for imp in implementation_of_academic_plan:
                # создаем список направлений + уп с айдишниками ИСУ для БАРСа
                field_of_studies = FieldOfStudy.objects.get(
                    implementation_academic_plan_in_field_of_study=imp)
                imp_list.append(generate_fos(imp.ns_id, field_of_studies.number, imp.title))
                isu_wp = \
                    list(WorkProgramIdStrUpForIsu.objects.filter(
                        work_program_in_field_of_study__work_program=work_program,
                        work_program_in_field_of_study__work_program_change_in_discipline_block_module__discipline_block_module__descipline_block__academic_plan__academic_plan_in_field_of_study=imp))[
                        0]
                isu_wp_id = isu_wp.dis_id

            imp_list = list({v['id']: v for v in imp_list}.values())  # Оставляем уникальные значения по айдишникам

            if imp_list and now_semester % 2 == send_semester:  # Если такой существует и соотвествует весне/осени (
                # Генерируем чекпоинт со всеми УП, прямыми и относиетльным семестром

                request_text = generate_single_checkpoint(absolute_semester=now_semester + 1,
                                                          relative_semester=count_relative,
                                                          programs=imp_list,
                                                          work_program=work_program, setup=setup_bars,
                                                          wp_isu_id=isu_wp_id, types_checkpoints=types_checkpoints)
                isu_wp = None
                isu_wp_id = None
                # Получаем вернувшуюся информацию
                # print(request_text)
                request_response, request_status_code = post_checkpoint_plan(request_text, setup_bars)
                if request_status_code != 200:
                    #  если почему-то не отправилось продублируем респонс в терминал
                    print(request_text, request_response)
                # Пишем логи
                HistoryOfSendingToBars.objects.create(work_program=work_program, request_text=request_text,
                                                      request_response=request_response,
                                                      request_status=request_status_code)
                all_sends.append(
                    {"status": request_status_code, "request": request_text, "response": request_response})
            # Если дисциплина длинной несколько семестров, то добавляем плюсик к счетчику относительного семестра
            if implementation_of_academic_plan_all and not relative_bool:
                count_relative += 1
    return Response(all_sends)


class BarsHistoryListView(generics.ListAPIView):
    queryset = HistoryOfSendingToBars.objects.all()
    serializer_class = HistoryOfSendingBarsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['date_of_sending', 'work_program', "request_status"]
    search_fields = ["date_of_sending", "work_program", "request_status"]
    permission_classes = [IsAdminUser]


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def SetBarsPointerTrueToWP(request):
    for semester in range(0, 4):
        cred_regex = r""
        for i in range(12):
            if i == semester:
                cred_regex += "[^0]\.[0-9],\s"
            else:
                cred_regex += "(([0-9]\.[0-9])|[0]),\s"
        cred_regex = cred_regex[:-3]
        wp = WorkProgram.objects.filter(zuns_for_wp__zuns_for_wp__ze_v_sem__iregex=cred_regex,
                                        expertise_with_rpd__expertise_status__contains='AC',
                                        zuns_for_wp__work_program_change_in_discipline_block_module__discipline_block_module__descipline_block__academic_plan__academic_plan_in_field_of_study__qualification="bachelor").distinct()
        wp.update(bars=True)
    return Response("Надеюсь, ничего не сломалось")
