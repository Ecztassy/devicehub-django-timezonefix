import os
import tarfile
import tempfile

from django.conf import settings
from django.core.files.storage import storages
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Restore an evidence backup from the dbbackup storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input-filename',
            help='Name of the backup file to restore. Defaults to the most recent one.',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available evidence backups.',
        )

    def handle(self, *args, **options):
        storage = storages['dbbackup']

        if options['list']:
            self._list_backups(storage)
            return

        filename = options['input_filename'] or self._get_latest(storage)
        if not filename:
            raise CommandError('No evidence backups found.')

        self.stdout.write(f'Restoring from {filename}...')

        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with storage.open(filename, 'rb') as src:
                with open(tmp_path, 'wb') as dst:
                    dst.write(src.read())

            evidences_dir = settings.EVIDENCES_DIR
            with tarfile.open(tmp_path, 'r:gz') as tar:
                tar.extractall(path=os.path.dirname(os.path.abspath(evidences_dir)))

            self.stdout.write(self.style.SUCCESS(
                f'Evidences restored to {evidences_dir}'
            ))
        finally:
            os.unlink(tmp_path)

    def _list_backups(self, storage):
        _, files = storage.listdir('.')
        backups = sorted(f for f in files if f.startswith('evidences-') and f.endswith('.tar.gz'))
        if not backups:
            self.stdout.write('No evidence backups available.')
            return
        self.stdout.write('Available backups:')
        for f in backups:
            self.stdout.write(f'  {f}')

    def _get_latest(self, storage):
        _, files = storage.listdir('.')
        backups = sorted(f for f in files if f.startswith('evidences-') and f.endswith('.tar.gz'))
        return backups[-1] if backups else None
