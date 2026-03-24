import os
import tarfile
import tempfile
from datetime import datetime

from django.conf import settings
from django.core.files.storage import storages
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backup the evidences directory (snapshots) to the dbbackup storage'

    def handle(self, *args, **options):
        evidences_dir = settings.EVIDENCES_DIR
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = f'evidences-{timestamp}.tar.gz'

        self.stdout.write(f'Creating backup of {evidences_dir}...')

        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with tarfile.open(tmp_path, 'w:gz') as tar:
                tar.add(evidences_dir, arcname=os.path.basename(evidences_dir))

            storage = storages['dbbackup']
            with open(tmp_path, 'rb') as f:
                saved_name = storage.save(filename, f)

            size_mb = os.path.getsize(tmp_path) / (1024 * 1024)
            self.stdout.write(self.style.SUCCESS(
                f'Backup saved: {saved_name} ({size_mb:.1f} MB)'
            ))
        finally:
          os.unlink(tmp_path)
