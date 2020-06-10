import {createLogic} from "redux-logic";

import actions from '../../../layout/actions';
import workProgramActions from '../actions';

import Service from '../service';
import {getWorkProgramId} from '../getters';

import {fetchingTypes, fields} from "../enum";

const service = new Service();

const addEvaluationTool = createLogic({
    type: workProgramActions.addEvaluationTool.type,
    latest: true,
    process({getState, action}: any, dispatch, done) {
        const evaluationTool = action.payload;

        dispatch(actions.fetchingTrue({destination: fetchingTypes.ADD_EVALUATION_TOOL}));

        service.addEvaluationTool(evaluationTool)
            .then((res) => {
                dispatch(workProgramActions.getWorkProgramEvaluationTools());
                // @ts-ignore
                dispatch(actions.fetchingSuccess());
                dispatch(workProgramActions.closeDialog(fields.CREATE_NEW_EVALUATION_TOOLS));
            })
            .catch((err) => {
                dispatch(actions.fetchingFailed(err));
            })
            .then(() => {
                dispatch(actions.fetchingFalse({destination: fetchingTypes.ADD_EVALUATION_TOOL}));
                return done();
            });
    }
});

const changeEvaluationTool = createLogic({
    type: workProgramActions.changeEvaluationTool.type,
    latest: true,
    process({getState, action}: any, dispatch, done) {
        const state = getState();
        const workProgramId = getWorkProgramId(state);
        const evaluationTool = action.payload;

        dispatch(actions.fetchingTrue({destination: fetchingTypes.CHANGE_EVALUATION_TOOL}));

        service.changeEvaluationTool(evaluationTool, workProgramId)
            .then((res) => {
                dispatch(workProgramActions.getWorkProgramEvaluationTools());
                // @ts-ignore
                dispatch(actions.fetchingSuccess());
                dispatch(workProgramActions.closeDialog(fields.CREATE_NEW_EVALUATION_TOOLS));
            })
            .catch((err) => {
                dispatch(actions.fetchingFailed(err));
            })
            .then(() => {
                dispatch(actions.fetchingFalse({destination: fetchingTypes.CHANGE_EVALUATION_TOOL}));
                return done();
            });
    }
});


const deleteEvaluationTool = createLogic({
    type: workProgramActions.deleteEvaluationTool.type,
    latest: true,
    process({getState, action}: any, dispatch, done) {
        const id = action.payload;

        dispatch(actions.fetchingTrue({destination: fetchingTypes.DELETE_EVALUATION_TOOL}));

        service.deleteEvaluationTool(id)
            .then((res) => {
                dispatch(workProgramActions.getWorkProgramEvaluationTools());
                // @ts-ignore
                dispatch(actions.fetchingSuccess());
            })
            .catch((err) => {
                dispatch(actions.fetchingFailed(err));
            })
            .then(() => {
                dispatch(actions.fetchingFalse({destination: fetchingTypes.DELETE_EVALUATION_TOOL}));
                return done();
            });
    }
});

export default [
    changeEvaluationTool,
    addEvaluationTool,
    deleteEvaluationTool,
];