from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from decimal import Decimal
from .models import Species, ConservationStatus, Occurrence, DataImportLog


class SpeciesModelTest(TestCase):
    """Test cases for Species model"""
    
    def setUp(self):
        self.species = Species.objects.create(
            taxon_key=12345,
            kingdom="Plantae",
            phylum="Tracheophyta",
            class_name="Magnoliopsida",
            order="Laurales",
            family="Lauraceae",
            genus="Persea",
            species="americana"
        )
    
    def test_species_creation(self):
        """Test that species is created correctly"""
        self.assertEqual(self.species.taxon_key, 12345)
        self.assertEqual(self.species.scientific_name, "Persea americana")
        self.assertEqual(str(self.species), "Persea americana")
    
    def test_scientific_name_generation(self):
        """Test that scientific name is auto-generated"""
        self.assertEqual(self.species.scientific_name, "Persea americana")
    
    def test_occurrence_count_property(self):
        """Test occurrence count property"""
        self.assertEqual(self.species.occurrence_count, 0)
        
        # Create an occurrence
        Occurrence.objects.create(
            gbif_id=67890,
            species=self.species,
            decimal_longitude=Decimal('-84.5'),
            decimal_latitude=Decimal('10.3'),
            scientific_name="Persea americana"
        )
        
        # Refresh from database
        self.species.refresh_from_db()
        self.assertEqual(self.species.occurrence_count, 1)


class ConservationStatusModelTest(TestCase):
    """Test cases for ConservationStatus model"""
    
    def setUp(self):
        self.species = Species.objects.create(
            taxon_key=12345,
            kingdom="Plantae",
            phylum="Tracheophyta",
            class_name="Magnoliopsida",
            order="Laurales",
            family="Lauraceae",
            genus="Persea",
            species="americana"
        )
        
        self.conservation_status = ConservationStatus.objects.create(
            species=self.species,
            rlcvs_status='PE',
            cites_status='AI',
            iucn_status='CR',
            endemic_to_acat=True
        )
    
    def test_conservation_status_creation(self):
        """Test that conservation status is created correctly"""
        self.assertEqual(self.conservation_status.species, self.species)
        self.assertEqual(self.conservation_status.rlcvs_status, 'PE')
        self.assertEqual(self.conservation_status.cites_status, 'AI')
        self.assertEqual(self.conservation_status.iucn_status, 'CR')
        self.assertTrue(self.conservation_status.endemic_to_acat)
    
    def test_is_threatened_property(self):
        """Test is_threatened property"""
        self.assertTrue(self.conservation_status.is_threatened)
        
        # Create non-threatened species
        non_threatened = ConservationStatus.objects.create(
            species=Species.objects.create(
                taxon_key=54321,
                kingdom="Plantae",
                phylum="Tracheophyta",
                class_name="Magnoliopsida",
                order="Rosales",
                family="Rosaceae",
                genus="Rosa",
                species="canina"
            ),
            rlcvs_status='NR',
            cites_status='NONE',
            iucn_status='LC'
        )
        
        self.assertFalse(non_threatened.is_threatened)


class OccurrenceModelTest(TestCase):
    """Test cases for Occurrence model"""
    
    def setUp(self):
        self.species = Species.objects.create(
            taxon_key=12345,
            kingdom="Plantae",
            phylum="Tracheophyta",
            class_name="Magnoliopsida",
            order="Laurales",
            family="Lauraceae",
            genus="Persea",
            species="americana"
        )
        
        self.occurrence = Occurrence.objects.create(
            gbif_id=67890,
            species=self.species,
            decimal_longitude=Decimal('-84.5'),
            decimal_latitude=Decimal('10.3'),
            scientific_name="Persea americana",
            locality="Monteverde"
        )
    
    def test_occurrence_creation(self):
        """Test that occurrence is created correctly"""
        self.assertEqual(self.occurrence.gbif_id, 67890)
        self.assertEqual(self.occurrence.species, self.species)
        self.assertEqual(self.occurrence.decimal_longitude, Decimal('-84.5'))
        self.assertEqual(self.occurrence.decimal_latitude, Decimal('10.3'))
    
    def test_location_auto_creation(self):
        """Test that Point geometry is auto-created from lat/lon"""
        self.assertIsNotNone(self.occurrence.location)
        self.assertEqual(self.occurrence.location.x, float(self.occurrence.decimal_longitude))
        self.assertEqual(self.occurrence.location.y, float(self.occurrence.decimal_latitude))
    
    def test_coordinate_validation(self):
        """Test coordinate validation"""
        # This should pass validation (within Costa Rica bounds)
        self.occurrence.clean()
        
        # This should fail validation (outside Costa Rica bounds)
        self.occurrence.decimal_latitude = Decimal('50.0')  # Too far north
        with self.assertRaises(Exception):
            self.occurrence.clean()


class BiodiversityViewsTest(TestCase):
    """Test cases for Biodiversity views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.species = Species.objects.create(
            taxon_key=12345,
            kingdom="Plantae",
            phylum="Tracheophyta",
            class_name="Magnoliopsida",
            order="Laurales",
            family="Lauraceae",
            genus="Persea",
            species="americana"
        )
        
        self.occurrence = Occurrence.objects.create(
            gbif_id=67890,
            species=self.species,
            decimal_longitude=Decimal('-84.5'),
            decimal_latitude=Decimal('10.3'),
            scientific_name="Persea americana"
        )
    
    def test_species_list_view(self):
        """Test species list view"""
        response = self.client.get(reverse('biodiversity:species_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Persea americana")
    
    def test_species_detail_view(self):
        """Test species detail view"""
        response = self.client.get(
            reverse('biodiversity:species_detail', kwargs={'pk': self.species.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Persea americana")
    
    def test_occurrence_list_view(self):
        """Test occurrence list view"""
        response = self.client.get(reverse('biodiversity:occurrence_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Persea americana")
    
    def test_occurrence_map_view(self):
        """Test occurrence map view"""
        response = self.client.get(reverse('biodiversity:occurrence_map'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mapa de Registros")
    
    def test_species_list_filtering(self):
        """Test species list filtering"""
        response = self.client.get(
            reverse('biodiversity:species_list') + '?family=Lauraceae'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Persea americana")
        
        response = self.client.get(
            reverse('biodiversity:species_list') + '?family=Rosaceae'
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Persea americana")


class DataImportLogTest(TestCase):
    """Test cases for DataImportLog model"""
    
    def test_import_log_creation(self):
        """Test import log creation and success rate calculation"""
        log = DataImportLog.objects.create(
            import_type='species',
            status=DataImportLog.StatusChoices.SUCCESS,
            records_processed=100,
            records_created=80,
            records_updated=15,
            records_errors=5,
            source_file='test_species.csv'
        )
        
        self.assertEqual(log.success_rate, 95.0)  # (100-5)/100 * 100
        self.assertEqual(str(log), "Importación de Especies - Exitoso")


class ManagementCommandTest(TestCase):
    """Test cases for management commands"""
    
    def test_import_command_exists(self):
        """Test that import_darwin_core command exists"""
        from django.core.management import get_commands
        commands = get_commands()
        self.assertIn('import_darwin_core', commands)
