import requests
from django.core.management.base import BaseCommand
from eoftermapp.models import EFOterm, ParentRelationship
from concurrent.futures import ThreadPoolExecutor, as_completed

class Command(BaseCommand):
    help = 'Import ontology terms from OLS API'

    def fetch_data(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error fetching data: {e}'))
            return None

    def handle(self, *args, **kwargs):
        OLS_API_URL = 'http://www.ebi.ac.uk/ols/api/ontologies/efo/terms?size=1000'
        has_more = True
        efo_term_cache = {}
        existing_efo_terms = {efo.efo_term_id: efo for efo in EFOterm.objects.all()}  # Fetch all terms as a dictionary

        with ThreadPoolExecutor() as executor:

            while has_more:
                to_create = []
                to_update = []
                data = self.fetch_data(OLS_API_URL)
                if not data:
                    break

                terms = data['_embedded']['terms']
                existing_efo_ids = set(existing_efo_terms.keys())

                future_to_term = {}

                for term in terms:
                    efo_id = term['obo_id']
                    if not efo_id:
                        self.stdout.write(self.style.ERROR(f'Skipping term with missing obo_id: {term}'))
                        continue  # skip this term entirely
                    parent_data_url = term.get('_links', {}).get('parents', {}).get('href')
                    if parent_data_url:
                        future = executor.submit(self.fetch_data, parent_data_url)
                        future_to_term[future] = term
                    else:
                        # Process terms without a parent link immediately
                        if efo_id not in existing_efo_ids:
                            efo_term = EFOterm(
                                efo_term_id=efo_id,
                                term_name=term['label'],
                                synonyms=term.get('synonyms', [])
                            )
                            to_create.append(efo_term)

                for future in as_completed(future_to_term):
                    term = future_to_term[future]
                    parent_data = future.result()
                    parent_id_list = [t['obo_id'] for t in parent_data['_embedded']['terms']] if parent_data else []

                    efo_id = term['obo_id']
                    if efo_id not in existing_efo_ids:
                        efo_term = EFOterm(
                            efo_term_id=efo_id,
                            term_name=term['label'],
                            synonyms=term.get('synonyms', [])
                        )
                        to_create.append(efo_term)
                        efo_term_cache[efo_id] = parent_id_list
                    else:
                        exist_efo_term = existing_efo_terms[efo_id]
                        exist_efo_term.term_name = term['label']
                        exist_efo_term.synonyms = term.get('synonyms', [])
                        to_update.append(exist_efo_term)
                        efo_term_cache[efo_id] = parent_id_list

                EFOterm.objects.bulk_create(to_create)
                EFOterm.objects.bulk_update(to_update, ['term_name', 'synonyms'])

                OLS_API_URL = data['_links'].get('next', {}).get('href')
                if not OLS_API_URL:
                    has_more = False

        # Create ParentRelationship records for each parent-child relationship
        for efo_term_id, parent_ids in efo_term_cache.items():
            child_term = EFOterm.objects.get(efo_term_id=efo_term_id)
            for parent_id in parent_ids:
                parent_term = existing_efo_terms.get(parent_id)
                if not parent_term:
                    continue  # skip if the parent doesn't exist in the local database
                ParentRelationship.objects.get_or_create(term=child_term, parent=parent_term)

        self.stdout.write(self.style.SUCCESS('Successfully imported ontology terms'))