export enum fields {
    TRAINING_MODULES_LIST = 'TRAINING_MODULES_LIST',
    DETAIL_TRAINING_MODULE = 'DETAIL_TRAINING_MODULE',
    SEARCH_QUERY = 'SEARCH_QUERY',
    CURRENT_PAGE = 'CURRENT_PAGE',
    ALL_COUNT = 'ALL_COUNT',
    SORTING = 'SORTING',
    SORTING_FIELD = 'SORTING_FIELD',
    SORTING_MODE = 'SORTING_MODE',
    TRAINING_MODULE_DIALOG = 'TRAINING_MODULE_DIALOG',
    IS_OPEN_TRAINING_MODULE_DIALOG = 'IS_OPEN_TRAINING_MODULE_DIALOG',
    TRAINING_MODULE_DIALOG_DATA = 'TRAINING_MODULE_DIALOG_DATA',
    SHOW_ONLY_MY = 'SHOW_ONLY_MY',
}

export enum fetchingTypes {
    GET_TRAINING_MODULE = 'GET_TRAINING_MODULE',
    GET_TRAINING_MODULES = 'GET_TRAINING_MODULES',
    CREATE_TRAINING_MODULE = 'CREATE_TRAINING_MODULE',
    CHANGE_TRAINING_MODULE = 'CHANGE_TRAINING_MODULE',
    DELETE_TRAINING_MODULE = 'DELETE_TRAINING_MODULE',
}

export enum TrainingModuleFields {
    ID = 'id',
    NAME = 'name',
    DESCRIPTION = 'description',
    DISCIPLINE = 'descipline_block',
    ACADEMIC_PLAN = 'academic_plan',
    EDUCATIONAL_PROFILE = 'educational_profile',
    ACADEMIC_PLAN_IN_FIELD_OF_STUDY = 'academic_plan_in_field_of_study',
    FIELD_OF_STUDY = 'field_of_study',
    TYPE = 'type',
    EDITORS = 'editors',
    CAN_EDIT = 'can_edit',
}
