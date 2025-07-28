import csv
import sqlite3
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone
from apps.biodiversity.models import Species, Occurrence, DataImportLog


class Command(BaseCommand):
    help = 'Import Darwin Core data from CSV and GeoPackage files'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--species-file',
            type=str,
            default='data/biodiversity/raw/especies.csv',
            help='Path to species CSV file'
        )
        parser.add_argument(
            '--occurrences-file',
            type=str,
            default='data/biodiversity/raw/registros-presencia.gpkg',
            help='Path to occurrences GeoPackage file'
        )
        parser.add_argument(
            '--import-type',
            choices=['species', 'occurrences', 'full'],
            default='full',
            help='Type of import to perform'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process in each batch'
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.batch_size = options['batch_size']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Create import log
        log = DataImportLog.objects.create(
            import_type=options['import_type'],
            source_file=f"{options['species_file']}, {options['occurrences_file']}",
            status=DataImportLog.StatusChoices.STARTED
        )
        
        try:
            if options['import_type'] in ['species', 'full']:
                self.import_species(options['species_file'], log)
            
            if options['import_type'] in ['occurrences', 'full']:
                self.import_occurrences(options['occurrences_file'], log)
            
            # Mark as successful
            log.status = DataImportLog.StatusChoices.SUCCESS
            log.completed_at = timezone.now()
            log.duration_seconds = (log.completed_at - log.started_at).total_seconds()
            
            if not self.dry_run:
                log.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported data. '
                    f'Species: {log.records_created} created, {log.records_updated} updated. '
                    f'Duration: {log.duration_seconds:.1f}s'
                )
            )
            
        except Exception as e:
            log.status = DataImportLog.StatusChoices.ERROR
            log.error_details = str(e)
            log.completed_at = timezone.now()
            
            if not self.dry_run:
                log.save()
            
            self.stdout.write(
                self.style.ERROR(f'Import failed: {str(e)}')
            )
            raise CommandError(f'Import failed: {str(e)}')
    
    def import_species(self, species_file, log):
        """Import species data from CSV file"""
        self.stdout.write(f'Importing species from {species_file}...')
        
        if not os.path.exists(species_file):
            raise CommandError(f'Species file not found: {species_file}')
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        with open(species_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            species_batch = []
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Parse taxonKey
                    taxon_key = int(row['taxonKey'])
                    
                    # Prepare species data
                    species_data = {
                        'taxon_key': taxon_key,
                        'kingdom': row.get('kingdom', '').strip(),
                        'phylum': row.get('phylum', '').strip(),
                        'class_name': row.get('class', '').strip(),
                        'order': row.get('order', '').strip(),
                        'family': row.get('family', '').strip(),
                        'genus': row.get('genus', '').strip(),
                        'species': row.get('species', '').strip(),
                        'last_gbif_update': timezone.now()
                    }
                    
                    if not self.dry_run:
                        # Use get_or_create for upsert behavior
                        species_obj, created = Species.objects.get_or_create(
                            taxon_key=taxon_key,
                            defaults=species_data
                        )
                        
                        if not created:
                            # Update existing species
                            for field, value in species_data.items():
                                setattr(species_obj, field, value)
                            species_obj.save()
                            updated_count += 1
                        else:
                            created_count += 1
                    else:
                        created_count += 1
                    
                    # Progress reporting
                    if row_num % self.batch_size == 0:
                        self.stdout.write(f'  Processed {row_num} species records...')
                
                except (ValueError, KeyError) as e:
                    error_count += 1
                    self.stderr.write(f'  Error in row {row_num}: {str(e)}')
                    log.log_messages += f'Species row {row_num} error: {str(e)}\n'
                    continue
        
        log.records_created += created_count
        log.records_updated += updated_count
        log.records_errors += error_count
        log.records_processed += created_count + updated_count + error_count
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Species import completed: {created_count} created, '
                f'{updated_count} updated, {error_count} errors'
            )
        )
    
    def import_occurrences(self, occurrences_file, log):
        """Import occurrence data from GeoPackage file"""
        self.stdout.write(f'Importing occurrences from {occurrences_file}...')
        
        if not os.path.exists(occurrences_file):
            raise CommandError(f'Occurrences file not found: {occurrences_file}')
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        # Connect to GeoPackage (SQLite database)
        conn = sqlite3.connect(occurrences_file)
        conn.row_factory = sqlite3.Row  # Access columns by name
        cursor = conn.cursor()
        
        try:
            # Get all occurrence records
            cursor.execute('SELECT * FROM "registros-presencia"')
            
            occurrence_batch = []
            batch_count = 0
            
            while True:
                rows = cursor.fetchmany(self.batch_size)
                if not rows:
                    break
                
                for row in rows:
                    try:
                        # Parse required fields
                        gbif_id = int(row['gbifID']) if row['gbifID'] else None
                        taxon_key = int(row['taxonKey']) if row['taxonKey'] else None
                        
                        if not gbif_id or not taxon_key:
                            error_count += 1
                            continue
                        
                        # Find corresponding species
                        try:
                            species = Species.objects.get(taxon_key=taxon_key)
                        except Species.DoesNotExist:
                            error_count += 1
                            log.log_messages += f'Species with taxonKey {taxon_key} not found for occurrence {gbif_id}\n'
                            continue
                        
                        # Parse coordinates
                        try:
                            decimal_longitude = Decimal(str(row['decimalLongitude']))
                            decimal_latitude = Decimal(str(row['decimalLatitude'])) 
                        except (InvalidOperation, TypeError, ValueError):
                            error_count += 1
                            log.log_messages += f'Invalid coordinates for occurrence {gbif_id}\n'
                            continue
                        
                        # Prepare occurrence data
                        occurrence_data = {
                            'gbif_id': gbif_id,
                            'species': species,
                            'dataset_key': row.get('datasetKey', ''),
                            'occurrence_id': row.get('occurrenceID', ''),
                            'decimal_longitude': decimal_longitude,
                            'decimal_latitude': decimal_latitude,
                            'scientific_name': row.get('scientificName', ''),
                            'taxon_rank': row.get('taxonRank', ''),
                            'country_code': row.get('countryCode', 'CR'),
                            'state_province': row.get('stateProvince', ''),
                            'locality': row.get('locality', ''),
                            'basis_of_record': row.get('basisOfRecord', ''),
                            'institution_code': row.get('institutionCode', ''),
                            'collection_code': row.get('collectionCode', ''),
                            'last_gbif_update': timezone.now()
                        }
                        
                        # Parse date fields
                        if row.get('eventDate'):
                            try:
                                # Handle different date formats
                                date_str = str(row['eventDate'])
                                if 'T' in date_str:
                                    date_str = date_str.split('T')[0]
                                occurrence_data['event_date'] = datetime.strptime(
                                    date_str, '%Y-%m-%d'
                                ).date()
                            except ValueError:
                                pass
                        
                        # Parse year, month, day
                        for field in ['year', 'month', 'day']:
                            if row.get(field):
                                try:
                                    occurrence_data[field] = int(row[field])
                                except (ValueError, TypeError):
                                    pass
                        
                        if not self.dry_run:
                            # Use get_or_create for upsert behavior
                            occurrence_obj, created = Occurrence.objects.get_or_create(
                                gbif_id=gbif_id,
                                defaults=occurrence_data
                            )
                            
                            if not created:
                                # Update existing occurrence
                                for field, value in occurrence_data.items():
                                    setattr(occurrence_obj, field, value)
                                occurrence_obj.save()
                                updated_count += 1
                            else:
                                created_count += 1
                        else:
                            created_count += 1
                    
                    except Exception as e:
                        error_count += 1
                        self.stderr.write(f'  Error processing occurrence {gbif_id}: {str(e)}')
                        log.log_messages += f'Occurrence {gbif_id} error: {str(e)}\n'
                        continue
                
                batch_count += len(rows)
                self.stdout.write(f'  Processed {batch_count} occurrence records...')
        
        finally:
            conn.close()
        
        log.records_created += created_count
        log.records_updated += updated_count
        log.records_errors += error_count
        log.records_processed += created_count + updated_count + error_count
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Occurrences import completed: {created_count} created, '
                f'{updated_count} updated, {error_count} errors'
            )
        )
