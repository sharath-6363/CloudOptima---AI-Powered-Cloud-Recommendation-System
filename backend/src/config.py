# Configuration constants
DATA_DIR = "data"
CRITERIA_NAMES = ['Cost', 'CPU', 'RAM', 'Storage', 'Security']
CRITERIA_TYPES = ['cost', 'benefit', 'benefit', 'benefit', 'benefit']
DEFAULT_WEIGHTS = [0.3, 0.2, 0.2, 0.1, 0.2]  # cost, cpu, ram, storage, security

# Cloud provider configurations
PROVIDER_CONFIGS = {
    'AWS': {
        'color': '#FF9900',
        'regions': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-south-1']
    },
    'Azure': {
        'color': '#0078D4',
        'regions': ['eastus', 'westus', 'northeurope', 'southeastasia']
    },
    'GCP': {
        'color': '#4285F4', 
        'regions': ['us-central1', 'europe-west1', 'asia-southeast1']
    }
}