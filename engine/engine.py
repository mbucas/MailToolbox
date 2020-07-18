#!/usr/bin/python
# coding:utf8


class Engine(object):
    """
        Engine
        Class that moves mails
    """
    def __init__(self, project, folderCallback=None, mailCallback=None):
        self.project = project
        if callable(folderCallback):
            self.folderCallback = folderCallback
        else:
            self.folderCallback = None
        if callable(mailCallback):
            self.mailCallback = mailCallback
        else:
            self.mailCallback = None

    def run(self):
        self.project.source.openSession()
        self.project.target.openSession()
        for transformation in self.project.transformations:
            transformation.prepare_run()
        # Read all folders from the source
        for folder in self.project.source.getFolders():
            if self.folderCallback:
                self.folderCallback(folder)
            # Read all mail in folder
            for mail in self.project.source.getFolderMailbox(folder):
                if self.mailCallback:
                    self.mailCallback(mail)

                # Don't overwrite loop values (I don't know what could happen)
                target_folder = folder
                target_mail = mail

                # Apply all transformations
                for transformation in self.project.transformations:
                    if target_folder and target_mail:
                        target_folder, target_mail = (
                            transformation.transform(
                                target_folder,
                                target_mail
                            )
                        )
                    else:
                        break

                # Filter transformations set values to None to discard data
                if (target_folder is not None) and (target_mail is not None):

                    # Apply mail in target storage

                    # Target folder can be different for each mail
                    # due to transformations, check every time
                    if not self.project.target.hasFolder(target_folder):
                        self.project.target.createFolder(target_folder)
                    mailboxTarget = (
                        self
                        .project
                        .target
                        .getFolderMailbox(target_folder)
                    )

                    # Get action to apply
                    action = self.project.target.properties['action']
                    if action == 'data driven':
                        action = target_mail.action

                    # Apply action
                    if action == 'add':
                        mailboxTarget.add(target_mail)
                    elif action == 'remove':
                        mailboxTarget.remove(target_mail)
                    elif action == 'update':
                        mailboxTarget.update(target_mail)
                    else:  # TODO Not the correct Exception type
                        raise NotImplementedError(
                            'Action unknown' + target_mail.action
                        )

        self.project.source.closeSession()
        self.project.target.closeSession()
