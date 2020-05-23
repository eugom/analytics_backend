import React from 'react';

// @ts-ignore
import Link from "react-router-dom/Link";

import List from "@material-ui/core/List";
import ListItemText from "@material-ui/core/ListItemText";
import ListItem from "@material-ui/core/ListItem";
import Button from "@material-ui/core/Button";
import Divider from "@material-ui/core/Divider";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import withStyles from '@material-ui/core/styles/withStyles';

import AddIcon from "@material-ui/icons/Add";

import {FourthStepProps} from './types';
import {workProgramSectionFields, workProgramTopicFields} from "../enum";

import connect from './FourthStep.connect';
import styles from './FourthStep.styles';
import IconButton from "@material-ui/core/IconButton";
import DeleteIcon from "@material-ui/icons/DeleteOutlined";
import EditIcon from "@material-ui/icons/EditOutlined";
import ThemeCreateModal from "./ThemeCreateModal";
import DragIndicatorIcon from "@material-ui/icons/DragIndicator";
import Fab from "@material-ui/core/Fab";

class FourthStep extends React.PureComponent<FourthStepProps> {
    state = {
        isOpenCreateModal: false
    };

    handleCreateNewTopic = () => {
        this.setState({isOpenCreateModal: true});
    };

    closeCreateNewTopicModal = () => {
        this.setState({isOpenCreateModal: false});
    };

    handleClickDelete = () => {

    };

    handleClickEdit = () => {

    };

    render() {
        const {classes, sections} = this.props;
        const {isOpenCreateModal} = this.state;

        return (
            <div className={classes.topicsSection}>
                <div className={classes.topicsList}>
                    {sections.map(section => (
                        <div className={classes.sectionItem}>
                            <Typography className={classes.sectionTitle}>
                                {section[workProgramSectionFields.ORDINAL_NUMBER]}. {section[workProgramSectionFields.NAME]}
                            </Typography>

                            <div className={classes.topicsSectionList}>
                                {section[workProgramSectionFields.TOPICS].length === 0 &&
                                    <div>
                                        <div className={classes.topic}>
                                            <Typography className={classes.topicName}>
                                                В этом разделе пока не создано тем
                                            </Typography>
                                        </div>
                                    </div>
                                }
                                {section[workProgramSectionFields.TOPICS].map(topic =>
                                    <div className={classes.topic}>
                                        <DragIndicatorIcon style={{cursor: "pointer"}}/>

                                        <Typography className={classes.topicName}>
                                            {section[workProgramSectionFields.ORDINAL_NUMBER]}.
                                            {topic[workProgramTopicFields.NUMBER]}. {topic[workProgramTopicFields.DESCRIPTION]}
                                        </Typography>

                                        <div className={classes.onlineCourseItem}>
                                            <Typography>Онлайн курс: </Typography>&nbsp;
                                            <Link to={"/"} className={classes.link}>
                                                <Typography> название курса </Typography>
                                            </Link>
                                        </div>

                                        <div className={classes.actions}>
                                            <IconButton onClick={this.handleClickDelete}>
                                                <DeleteIcon />
                                            </IconButton>
                                            <IconButton onClick={this.handleClickEdit}>
                                                <EditIcon />
                                            </IconButton>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                <Fab color="secondary"
                     className={classes.addIcon}
                     onClick={this.handleCreateNewTopic}
                >
                    <AddIcon/>
                </Fab>

                <ThemeCreateModal isOpen={isOpenCreateModal} handleClose={this.closeCreateNewTopicModal} />
            </div>
        );
    }
}

export default connect(withStyles(styles)(FourthStep));
