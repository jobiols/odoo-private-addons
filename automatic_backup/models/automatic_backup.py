# For copyright and license notices, see __manifest__.py file in module root

import ftplib
import os
import re
import pickle
import tempfile
import base64
import mimetypes
from datetime import datetime
from datetime import date, timedelta

from os import listdir
from os.path import isfile, join
import odoo
from odoo import fields, models, api, exceptions
from odoo.tools.translate import _
from odoo.exceptions import UserError

BACKUP_PATTERN = r".*_\d\d\d\d-\d\d-\d\d_\d\d-\d\d-\d\d.(zip|dump)$"

NO_DROPBOX = False
try:
    import dropbox
except ImportError:
    NO_DROPBOX = True

NO_PYDRIVE = False
try:
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from pydrive.files import GoogleDriveFile

    def SetContentFile2(self, content, filename):
        self.content = content
        if self.get('title') is None:
            self['title'] = filename
        if self.get('mimeType') is None:
            self['mimeType'] = mimetypes.guess_type(filename)[0]

    GoogleDriveFile.SetContentFile2 = SetContentFile2

except ImportError:
    NO_PYDRIVE = True

NO_PYSFTP = False
try:
    import pysftp
except ImportError:
    NO_PYSFTP = True

NO_BOTO3 = False
try:
    import boto3
except ImportError:
    NO_BOTO3 = True


class AutomaticBackup(models.Model):

    _name = 'automatic.backup'
    _description = 'Automatic Backup'
    _inherit = ['mail.thread']

    name = fields.Char(
        default='Automatic Backup'
    )
    automatic_backup_rule_ids = fields.One2many(
        'ir.cron',
        'automatic_backup_id',
        string='Automatic Backup Rule'
    )
    successful_backup_notify_emails = fields.Char(
        string='Successful Backup Notification'
    )
    failed_backup_notify_emails = fields.Char(
        string='Failed Backup Notification'
    )
    delete_old_backups = fields.Boolean(
        default=False
    )
    filename = fields.Char(
        default=lambda self: self.env.cr.dbname
    )
    delete_days = fields.Integer(
        string='Delete backups older than [days]',
        default=30
    )

    @api.constrains('delete_days')
    def constrains_delete_days(self):
        for rec in self:
            if rec.delete_old_backups:
                if not rec.delete_days or rec.delete_days < 1:
                    raise exceptions.ValidationError(_('Minimal Delete Days = 1'))


class Cron(models.Model):

    _inherit = 'ir.cron'

    folder_path = fields.Char(
        default='/var/odoo/backups/'
    )
    ftp_address = fields.Char(
        string='URL'
    )
    ftp_port = fields.Integer(
        string='Port'
    )
    ftp_login = fields.Char(
        string='Login'
    )
    ftp_password = fields.Char(
        string='Password'
    )
    ftp_path = fields.Char(
        string='Path'
    )
    dropbox_authorize_url = fields.Char(
        string='Authorize URL'
    )
    dropbox_authorize_url_rel = fields.Char(

    )
    dropbox_authorization_code = fields.Char(
        string='Authorization Code'
    )
    dropbox_flow = fields.Integer(

    )
    dropbox_access_token = fields.Char(

    )
    dropbox_user_id = fields.Char(

    )
    dropbox_path = fields.Char(
        default='/Odoo Automatic Backups/',
        string='Backup Path'
    )
    s3_bucket_name = fields.Char(
        string='Bucket name'
    )
    s3_username = fields.Char(
        string='Username'
    )
    s3_access_key = fields.Char(
        string='Access key'
    )
    s3_access_key_secret = fields.Char(
        string='Acces key secret'
    )
    automatic_backup_id = fields.Many2one(
        'automatic.backup'
    )
    backup_type = fields.Selection(
        [
            ('dump', 'Database Only'),
            ('zip', 'Database and Filestore')
        ],
    )
    backup_destination = fields.Selection(
        [
            ('folder', 'Folder'),
            # ('ftp', 'FTP'),
            # ('sftp', 'SFTP'),
            # ('dropbox', 'Dropbox'),
            # ('google_drive', 'Google Drive'),
            ('s3', 'Amazon S3'),
        ]
    )

    @api.model
    def create(self, vals):
        """ Formatea y carga datos al generar el registro de cron
        """
        if 'dropbox_authorize_url_rel' in vals:
            vals['dropbox_authorize_url'] = vals['dropbox_authorize_url_rel']
        if 'backup_type' in vals:
            vals['name'] = 'Backup %s %s' % (vals['backup_type'],
                                             vals['backup_destination'])
            vals['numbercall'] = -1
            vals['state'] = 'code'
            vals['code'] = ''
            domain = [('model', '=', 'ir.cron')]
            vals['model_id'] = self.env['ir.model'].search(domain).id
        if 'folder_path' in vals:
            if not vals['folder_path'].endswith('/'):
                vals['folder_path'] += '/'

        output = super().create(vals)
        if 'backup_type' in vals:
            _ = "env['ir.cron'].database_backup_cron_action(' + str(output.id) + ')"
            output.code = _
        return output

    def write(self, vals):
        if 'dropbox_authorize_url_rel' in vals:
            vals['dropbox_authorize_url'] = vals['dropbox_authorize_url_rel']
        if 'folder_path' in vals:
            if not vals['folder_path'].endswith('/'):
                vals['folder_path'] += '/'
        return super().write(vals)

    def unlink(self):
        # delete flow/auth files
        for rec in self:
            self.env['ir.attachment'].browse(rec.dropbox_flow).unlink()
            output = super().unlink()
        return output

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'backup_rule' in self.env.context:
            args += ['|', ('active', '=', True), ('active', '=', False)]
        return super().search(args, offset, limit, order, count=count)

    @api.constrains('backup_type', 'backup_destination')
    def create_name(self):
        for rec in self:
            rec.name = 'Backup ' + rec.backup_type + ' ' + rec.backup_destination

    @api.onchange('backup_destination')
    def onchange_backup_destination(self):
        if self.backup_destination == 'ftp':
            self.ftp_port = 21

        if self.backup_destination == 'sftp':
            self.ftp_port = 22
            if NO_PYSFTP:
                raise exceptions.Warning(_('Missing required pysftp python package\n'
                                           'https://pypi.python.org/pypi/pysftp'))

        if self.backup_destination == 'dropbox':
            if NO_DROPBOX:
                raise exceptions.Warning(_('Missing required dropbox python package\n'
                                           'https://pypi.python.org/pypi/dropbox'))
            flow = dropbox.DropboxOAuth2FlowNoRedirect('jqurrm8ot7hmvzh',
                                                       '7u0goz5nmkgr1ot')
            self.dropbox_authorize_url = flow.start()
            self.dropbox_authorize_url_rel = self.dropbox_authorize_url

            self.dropbox_flow = self.env['ir.attachment'].create(dict(
                datas=base64.b64encode(pickle.dumps(flow)),
                name='dropbox_flow',
                datas_fname='dropbox_flow',
                description='Automatic Backup File'
            )).id

        if self.backup_destination == 'google_drive':
            if NO_PYDRIVE:
                raise exceptions.Warning(_('Missing required PyDrive python package\n'
                                           'https://pypi.python.org/pypi/PyDrive'))
            secrets_path = os.path.dirname(
                os.path.realpath(__file__)) + os.sep + '..' + os.sep + 'data' + os.sep + 'client_secrets.json'
            GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = secrets_path

            gauth = GoogleAuth()
            self.dropbox_authorize_url = gauth.GetAuthUrl()
            self.dropbox_authorize_url_rel = self.dropbox_authorize_url
            self.dropbox_flow = self.dropbox_flow = self.env['ir.attachment'].create(dict(
                datas=base64.b64encode(pickle.dumps(gauth)),
                name='dropbox_flow',
                datas_fname='dropbox_flow',
                description='Automatic Backup File'
            )).id

    @api.constrains('backup_destination', 'dropbox_authorization_code', 'dropbox_flow')
    def constrains_dropbox(self):
        for rec in self:
            if rec.backup_destination == 'sftp':
                if NO_PYSFTP:
                    raise exceptions.Warning(_('Missing required pysftp python '
                                               'package\n'
                                               'https://pypi.python.org/pypi/pysftp'))

            if rec.backup_destination == 'dropbox':
                if NO_DROPBOX:
                    raise exceptions.Warning(_('Missing required dropbox python '
                                               'package\n'
                                               'https://pypi.python.org/pypi/dropbox'))

                ia = self.env['ir.attachment'].browse(rec.dropbox_flow)
                ia.res_model = 'ir.cron'
                ia.res_id = rec.id

                flow = pickle.loads(base64.b64decode(ia.datas))
                result = flow.finish(rec.dropbox_authorization_code.strip())
                rec.dropbox_access_token = result.access_token
                rec.dropbox_user_id = result.user_id

            if rec.backup_destination == 'google_drive':
                if NO_PYDRIVE:
                    raise exceptions.Warning(_('Missing required PyDrive python '
                                               'package\n'
                                               'https://pypi.python.org/pypi/PyDrive'))

                ia = self.env['ir.attachment'].browse(rec.dropbox_flow)
                ia.res_model = 'ir.cron'
                ia.res_id = rec.id
                gauth = pickle.loads(base64.b64decode(ia.datas))
                gauth.Auth(rec.dropbox_authorization_code)
                ia.datas = base64.b64encode(pickle.dumps(gauth))

            if rec.backup_destination == 's3':
                if NO_BOTO3:
                    raise exceptions.Warning(_('Missing required boto3 python package\n'
                                               'https://pypi.python.org/pypi/boto3'))

    def check_settings(self):
        self.ensure_one()
        ret = self.create_backup(check=True)
        if ret == 'TestOk':
            return {
                'effect': {
                    'fadeout': 'slow',
                    'Message': 'Configuration is OK!',
                    'type': 'rainbow_man',
                }
            }

    def backup_btn(self):
        for rec in self:
            rec.create_backup()

    def get_selection_field_value(self, field, key):
        my_model_obj = self
        return dict(my_model_obj.fields_get(allfields=[field])[field]['selection'])[key]

    def show_rule_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Backup Rule',
            'res_model': 'ir.cron',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    def creation_time(self, fname):
        """ calcula el tiempo de creacion del archivo
        """
        secs = os.path.getctime(self.folder_path + fname)
        return datetime.fromtimestamp(secs)

    def build_filename(self):
        """ Crear el filename del backup
        """
        return '%s%s_%s.%s' % (
            self.folder_path,
            self.automatic_backup_id.filename,
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
            self.backup_type)

    def build_filename_s3(self):
        return '%s_%s.%s' % (self.automatic_backup_id.filename,
                             str(datetime.now()).split('.')[0].replace(':', '_'),
                             self.backup_type)

    def create_s3_backup(self, backup_binary):
        """ Manda el backup a un bucket s3 y hace limpieza
        """
        # nombre del archivo que va al bucket
        filename = self.build_filename_s3()

        # abrimos conexion a s3
        s3 = boto3.resource('s3',
                            aws_access_key_id=self.s3_access_key,
                            aws_secret_access_key=self.s3_access_key_secret)

        # metemos el archivo
        key = 'Odoo Automatic Backup/%s' % filename
        s3.Bucket(self.s3_bucket_name).put_object(Key=key, Body=backup_binary)

        # hacemos limpieza
        if self.automatic_backup_id.delete_old_backups:
            for o in s3.Bucket(self.s3_bucket_name).objects.all():
                if o.key.startswith('Odoo Automatic Backup/'):
                    filedate = o.last_modified.date()
                    delta = timedelta(days=self.automatic_backup_id.delete_days)
                    if filedate + delta < date.today():
                        self.file_delete_message(o.key)
                        o.delete()

        # notificamos finalizacion del backup
        self.success_message(os.path.basename(filename))

    def create_folder_backup(self, backup_binary, check=False):
        """ Manda el backup a un folder y hace la limpieza
        """
        filename = self.build_filename()
        try:
            with open(filename, 'wb') as f:
                f.write(backup_binary.read())

            if check:
                # si es un chequeo lo borro
                os.remove(filename)

        except (FileNotFoundError, PermissionError) as ex:
            if isinstance(ex, PermissionError):
                raise UserError(_('Can not open folder %s. '
                                    'Permission denied') % self.folder_path)
            if isinstance(ex, FileNotFoundError):
                raise UserError(_('Can not access %s. '
                                    'File or folder not found') % self.folder_path)

        # Si hay que borrar chequeo por archivos obsoletos y los borro
        if self.automatic_backup_id.delete_old_backups:
            files = [f for f in listdir(self.folder_path) \
                if isfile(join(self.folder_path, f))]

            for backup in files:
                if re.match(BACKUP_PATTERN, backup):
                    filedate = self.creation_time(backup)
                    delta = timedelta(days=self.automatic_backup_id.delete_days)
                    if filedate + delta < datetime.today():
                        os.remove(backup)
                        self.file_delete_message(self.folder_path + backup)

        # notificamos finalizacion del backup
        self.success_message(os.path.basename(filename))

    def create_ftp_backup(self, backup_binary, check=False):
        """ Manda el backup a ftp y hace la limpieza
        """
        filename = self.automatic_backup_id.filename + '_' + str(datetime.now()).split('.')[0].replace(':', '_') \
                    + '.' + self.backup_type
        ftp = ftplib.FTP()
        ftp.connect(self.ftp_address, self.ftp_port)
        ftp.login(self.ftp_login, self.ftp_password)
        ftp.cwd(self.ftp_path)
        ftp.storbinary('STOR ' + filename, backup_binary)
        if check is True:
            ftp.delete(filename)
        if self.automatic_backup_id.delete_old_backups:
            for backup in ftp.nlst():
                if re.match(BACKUP_PATTERN, backup) is not None:
                    px = len(backup) - 24
                    if backup.endswith('.dump'):
                        px -= 1
                    filedate = date(int(backup[px + 1:px + 5]), int(backup[px + 6:px + 8]), int(backup[px + 9:px + 11]))
                    if filedate + timedelta(days=self.automatic_backup_id.delete_days) < date.today():
                        ftp.delete(backup)
                        self.file_delete_message(backup)

        # notificamos finalizacion del backup
        self.success_message(os.path.basename(filename))

    def create_sftp_backup(self, backup_binary, check=False):
        """ Manda el backup a sftp y hace la limpieza
        """
        filename = self.automatic_backup_id.filename + '_' + str(datetime.now()).split('.')[0].replace(':', '_') \
                    + '.' + self.backup_type

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(self.ftp_address, username=self.ftp_login,
                                 password=self.ftp_password, cnopts=cnopts,
                                 port=self.ftp_port)
        sftp.putfo(backup_binary, self.ftp_path + '/' + filename)
        if check is True:
            sftp.remove(self.ftp_path + '/' + filename)
        if self.automatic_backup_id.delete_old_backups:
            for backup in sftp.listdir(self.ftp_path):
                if re.match(BACKUP_PATTERN, backup) is not None:
                    px = len(backup) - 24
                    if backup.endswith('.dump'):
                        px -= 1
                    filedate = date(int(backup[px + 1:px + 5]), int(backup[px + 6:px + 8]),
                                    int(backup[px + 9:px + 11]))
                    if filedate + timedelta(days=self.automatic_backup_id.delete_days) < date.today():
                        sftp.remove(self.ftp_path + '/' + backup)
                        self.file_delete_message(backup)

        # notificamos finalizacion del backup
        self.success_message(os.path.basename(filename))


    def create_dropbox_backup(self, backup_binary, check=False):
        """ Manda el backup a dropbox y hace la limpieza
        """
        filename = self.automatic_backup_id.filename + '_' + str(datetime.now()).split('.')[0].replace(':', '_') \
                    + '.' + self.backup_type
        client = dropbox.Dropbox(self.dropbox_access_token)
        client.files_upload(backup_binary.read(), '/' + filename)
        if check is True:
            client.files_delete_v2('/' + filename)
        if self.automatic_backup_id.delete_old_backups:
            for f in client.files_list_folder('').entries:
                if re.match(BACKUP_PATTERN, f.name) is not None:
                    px = len(f.name) - 24
                    if f.name.endswith('.dump'):
                        px -= 1
                    filedate = date(int(f.name[px + 1:px + 5]), int(f.name[px + 6:px + 8]), int(f.name[px + 9:px + 11]))
                    if filedate + timedelta(days=self.automatic_backup_id.delete_days) < date.today():
                        client.files_delete_v2('/' + f.name)
                        self.file_delete_message(f.name[1:])

        # notificamos finalizacion del backup
        self.success_message(os.path.basename(filename))

    def create_google_drive_backup(self, backup_binary, check=False):
        """ Manda el backup a google_drive y hace la limpieza
        """
        filename = self.automatic_backup_id.filename + '_' + str(datetime.now()).split('.')[0].replace(':', '_') \
                    + '.' + self.backup_type

        ia = self.env['ir.attachment'].browse(self.dropbox_flow)
        gauth = pickle.loads(base64.b64decode(ia.datas))
        drive = GoogleDrive(gauth)

        def getFolderID(folder_id, parent):
            file_list = drive.ListFile(
                {'q': "'" + parent + "' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
                        "and title='" + folder_id + "'"}).GetList()
            for file1 in file_list:
                if file1['title'] == folder_id:
                    return file1['id']
            folder_metadata = {'title': folder_id,
                                'mimeType': 'application/vnd.google-apps.folder',
                                'parents': [{'id': parent}]}
            folder = drive.CreateFile(folder_metadata)
            folder.Upload()
            return folder['id']

        def getFolderFromPath(path):
            folder_id = 'root'
            for p in path.split('/'):
                if not p:
                    continue
                folder_id = getFolderID(p, folder_id)
            return folder_id

        folderid = getFolderFromPath(self.dropbox_path)
        file1 = drive.CreateFile({'title': filename, 'parents': [{'kind': 'drive#fileLink', 'id': folderid}]})

        if self.backup_type == 'dump':
            # TODO: problems with to big files
            # _io.BufferedReader
            tmp_attachment = self.env['ir.attachment'].create({
                'datas': base64.b64encode(backup_binary.read()),
                'name': 'doc.dump',
                'datas_fname': 'doc.dump'
            })
            file1.SetContentFile(tmp_attachment._filestore() + os.sep + tmp_attachment.store_fname)
            file1.Upload()
            tmp_attachment.unlink()
        else:
            file1.SetContentFile2(backup_binary, 'binary.zip')
            file1.Upload()

        if check is True:
            file1.Delete()
        if self.automatic_backup_id.delete_old_backups:
            file_list = drive.ListFile({'q': "'" + folderid + "' in parents and trashed=false"}).GetList()
            for gfile in file_list:
                if re.match(BACKUP_PATTERN, gfile['title']) is not None:
                    px = len(gfile['title']) - 24
                    if gfile['title'].endswith('.dump'):
                        px -= 1
                    filedate = date(int(gfile['title'][px + 1:px + 5]), int(gfile['title'][px + 6:px + 8]), int(gfile['title'][px + 9:px + 11]))
                    if filedate + timedelta(days=self.automatic_backup_id.delete_days) < date.today():
                        drive.CreateFile({'id': gfile['id']}).Delete()
                        self.file_delete_message(gfile['title'])

        # notificamos finalizacion del backup
        self.success_message(os.path.basename(filename))

    def create_backup(self, check=False):
        """ Crea un backup en el destino programado,
            si check = True solamente chequea si puede hacerlo
        """
        if check:
            # Si estamos chequeando creo un backup_binary vacio
            backup_binary = tempfile.TemporaryFile()
            backup_binary.write(str.encode('Dummy File'))
            backup_binary.seek(0)
        else:
            # No estamos chequeando hago el backup
            backup_binary = odoo.service.db.dump_db(self.env.cr.dbname,
                                                    None,
                                                    self.backup_type)

        # delete unused flow/auth files
        domain = [('description', '=', 'Automatic Backup File'),
                  ('res_id', '=', False)]
        self.env['ir.attachment'].search(domain).unlink()

        if self.backup_destination == 'folder':
            self.create_folder_backup(backup_binary, check=check)

        if self.backup_destination == 'ftp':
            self.create_ftp_backup(backup_binary, check=check)

        if self.backup_destination == 'sftp':
            self.create_sftp_backup(backup_binary, check=check)

        if self.backup_destination == 'dropbox':
            self.create_dropbox_backup(backup_binary, check=check)

        if self.backup_destination == 'google_drive':
            self.create_google_drive_backup(backup_binary, check=check)

        if self.backup_destination == 's3':
            self.create_s3_backup(backup_binary)

        backup_binary.close()
        if check:
            return 'TestOk'

    def success_message(self, filename):
        msg = _('Backup created successfully!') + '<br/>'
        msg += _('Backup Type: ') + self.get_selection_field_value('backup_type', self.backup_type) + '<br/>'
        msg += _('Backup Destination: ') + self.get_selection_field_value('backup_destination',
                                                                          self.backup_destination) + '<br/>'
        if self.backup_destination == 'folder':
            msg += _('Folder Path: ') + self.folder_path + '<br/>'
        if self.backup_destination == 'ftp':
            msg += _('FTP Adress: ') + self.ftp_address + '<br/>'
            msg += _('FTP Path: ') + self.ftp_path + '<br/>'
        msg += _('Filename: ') + filename + '<br/>'
        self.env['mail.message'].create(dict(
            subject=_('Backup created successfully!'),
            body=msg,
            email_from=self.env['res.users'].browse(self.env.uid).email,
            model='automatic.backup',
            res_id=self.automatic_backup_id.id,
        ))
        if self.automatic_backup_id.successful_backup_notify_emails:
            self.env['mail.mail'].create(dict(
                subject=_('Backup created successfully!'),
                body_html=msg,
                email_from=self.env['res.users'].browse(self.env.uid).email,
                email_to=self.automatic_backup_id.successful_backup_notify_emails,
            )).send()

    def file_delete_message(self, filename):
        msg = _('Old backup deleted!') + '<br/>'
        msg += _('Backup Type: ') + self.get_selection_field_value('backup_type', self.backup_type) + '<br/>'
        msg += _('Backup Destination: ') + self.get_selection_field_value('backup_destination',
                                                                          self.backup_destination) + '<br/>'
        if self.backup_destination == 'folder':
            msg += _('Folder Path: ') + self.folder_path + '<br/>'
        if self.backup_destination == 'ftp':
            msg += _('FTP Adress: ') + self.ftp_address + '<br/>'
            msg += _('FTP Path: ') + self.ftp_path + '<br/>'
        msg += _('Filename: ') + filename + '<br/>'
        self.env['mail.message'].create(dict(
            subject=_('Old backup deleted!'),
            body=msg,
            email_from=self.env['res.users'].browse(self.env.uid).email,
            model='automatic.backup',
            res_id=self.automatic_backup_id.id,
        ))
        if self.automatic_backup_id.successful_backup_notify_emails:
            self.env['mail.mail'].create(dict(
                subject=_('Old backup deleted!'),
                body_html=msg,
                email_from=self.env['res.users'].browse(self.env.uid).email,
                email_to=self.automatic_backup_id.successful_backup_notify_emails,
            )).send()

    @api.model
    def database_backup_cron_action(self, *args):
        backup_rule = False
        try:
            if len(args) != 1 or isinstance(args[0], int) is False:
                raise exceptions.ValidationError(_('Wrong method parameters'))
            rule_id = args[0]
            backup_rule = self.browse(rule_id)
            backup_rule.create_backup()
        except Exception as e:
            msg = _('Automatic backup failed!') + '<br/>'
            msg += _('Backup Type: ') + backup_rule.get_selection_field_value('backup_type', backup_rule.backup_type) + '<br/>'
            msg += _('Backup Destination: ') + backup_rule.get_selection_field_value('backup_destination', backup_rule.backup_destination) + '<br/>'
            if backup_rule.backup_destination == 'folder':
                msg += _('Folder Path: ') + backup_rule.folder_path + '<br/>'
            if backup_rule.backup_destination == 'ftp':
                msg += _('FTP Adress: ') + backup_rule.ftp_address + '<br/>'
                msg += _('FTP Path: ') + backup_rule.ftp_path + '<br/>'
            msg += _('Exception: ') + str(e) + '<br/>'
            self.env['mail.message'].create(dict(
                subject=_('Automatic backup failed!'),
                body=msg,
                email_from=self.env['res.users'].browse(self.env.uid).email,
                model='automatic.backup',
                res_id=backup_rule.automatic_backup_id.id,
            ))
            if backup_rule.automatic_backup_id.failed_backup_notify_emails:
                self.env['mail.mail'].create(dict(
                    subject=_('Automatic backup failed!'),
                    body_html=msg,
                    email_from=self.env['res.users'].browse(self.env.uid).email,
                    email_to=backup_rule.automatic_backup_id.failed_backup_notify_emails,
                )).send()
