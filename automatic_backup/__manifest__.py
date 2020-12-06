{
    'name': 'Automatic Backup (Dropbox, Google Drive, Amazon S3, SFTP)',
    "license": "AGPL-3",
    'version': '11.0.1.0.0',
    'summary': 'Automatic Backup',
    'author': 'Grzegorz Krukar (grzegorzgk1@gmail.com), Jorge Obiols (jorge.obiols@gmail.com)',
    'data': [
        'data/data.xml',
        'views/automatic_backup.xml',
        'security/security.xml'
    ],
    'depends': [
        'mail',
    ],
    'external_dependencies': {
        'python': ['pydrive'],
    },
    'installable': True,
    'application': True,
}
